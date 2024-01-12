import requests
import time
from datetime import datetime
from dateutil import parser
from urllib.parse import parse_qs
from redash.query_runner import BaseQueryRunner, register, TYPE_DATETIME, TYPE_STRING
from redash.utils import json_dumps
from base64 import b64decode
from tempfile import NamedTemporaryFile
import os

def get_instant_rows(metrics_data):
    rows = []

    for metric in metrics_data:
        row_data = metric["metric"]

        timestamp, value = metric["value"]
        date_time = datetime.fromtimestamp(timestamp)

        row_data.update({"timestamp": date_time, "value": value})
        rows.append(row_data)
    return rows


def get_range_rows(metrics_data):
    rows = []

    for metric in metrics_data:
        ts_values = metric["values"]
        metric_labels = metric["metric"]

        for values in ts_values:
            row_data = metric_labels.copy()

            timestamp, value = values
            date_time = datetime.fromtimestamp(timestamp)

            row_data.update({"timestamp": date_time, "value": value})
            rows.append(row_data)
    return rows


# Convert datetime string to timestamp
def convert_query_range(payload):
    query_range = {}

    for key in ["start", "end"]:
        if key not in payload.keys():
            continue
        value = payload[key][0]

        if type(value) is str:
            # Don't convert timestamp string
            try:
                int(value)
                continue
            except ValueError:
                pass
            value = parser.parse(value)

        if type(value) is datetime:
            query_range[key] = [int(time.mktime(value.timetuple()))]

    payload.update(query_range)


def _create_cert_file(configuration, file_key, mtls_config):
    if file_key in configuration:
        with NamedTemporaryFile(mode="w", delete=False) as cert_file:
            cert_bytes = b64decode(configuration[file_key])
            cert_file.write(cert_bytes.decode("utf-8"))
        mtls_config[file_key] = cert_file.name


def _cleanup_mtls_certs(mtls_config):
    for k, v in mtls_config.items():
        if k != "mtls":
            os.remove(v)


def _get_mtls_config(configuration):
    use_mtls = configuration.get("mtls", "disable")
    if use_mtls == "require":
        mtls_config = {"mtls": use_mtls}
        _create_cert_file(configuration, "keyFile", mtls_config)
        _create_cert_file(configuration, "crtFile", mtls_config)
        _create_cert_file(configuration, "ca_crtFile", mtls_config)
        return mtls_config
    else:
        return None

class Prometheus(BaseQueryRunner):
    should_annotate_query = False

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {"url": {"type": "string", "title": "Prometheus API URL"},
                           "mtls": {
                               "type": "string",
                               "title": "Use mTLS",
                               "default": "disable",
                               "extendedEnum": [
                                   {"value": "disable", "name": "Disable"},
                                   {"value": "require", "name": "Require"},
                               ],
                           },
                           "user": {"type": "string", "title": "Username for Authentication"},
                           "password": {"type": "string", "title": "Password for Authentication"},
                           "keyFile": {"type": "string", "title": "Private Key to use with mtls Auth"},
                           "crtFile": {"type": "string", "title": "Signed certificate to use with  mtls Auth"},
                           "ca_crtFile": {"type": "string", "title": "Cert Authority Certificate to use with mtls Auth"}
            },
            "order": ["url", "user", "password", "mtls", "keyFile", "crtFile", "ca_crtFile"],
            "secret": ["password", "keyFile", "crtFile", "ca_crtFile"],
            "required": ["url"],
            "extra_options": [
                "mtls",
                "keyFile",
                "crtFile",
                "ca_crtFile",
            ],
        }

    def get_connection_auth(self):
        auth = None
        user = self.configuration.get("user", None)
        password = self.configuration.get("password", None)
        if user and password:
            auth = (user, password)

        mtls_config = _get_mtls_config(self.configuration)
        if mtls_config:
            cert = (mtls_config['crtFile'], mtls_config['keyFile'])
            verify = mtls_config['ca_crtFile']
        else:
            cert = None
            verify = None

        return auth, cert, verify, mtls_config

    def test_connection(self):
        auth, cert, verify, mtls_config = self.get_connection_auth()
        try:
            resp = requests.get(self.configuration.get("url", None), auth=auth, cert=cert, verify=verify)
        except Exception as e:
            raise Exception(f"Exception in validating Prometheus connector {e}") from e
        finally:
            _cleanup_mtls_certs(mtls_config)
        return resp.ok

    def get_schema(self, get_stats=False):
        base_url = self.configuration["url"]
        metrics_path = "/api/v1/label/__name__/values"
        auth, cert, verify, mtls_config = self.get_connection_auth()
        try:
            response = requests.get(base_url + metrics_path, auth=auth, cert=cert, verify=verify)
            response.raise_for_status()
            data = response.json()["data"]

            schema = {}
            for name in data:
                schema[name] = {"name": name, "columns": []}
            return list(schema.values())
        except Exception as e:
            raise Exception(f"Exception in getting schema from Prometheus connector {e}") from e
        finally:
            _cleanup_mtls_certs(mtls_config)

    def run_query(self, query, user):
        """
        Query Syntax, actually it is the URL query string.
        Check the Prometheus HTTP API for the details of the supported query string.

        https://prometheus.io/docs/prometheus/latest/querying/api/

        example: instant query
            query=http_requests_total

        example: range query
            query=http_requests_total&start=2018-01-20T00:00:00.000Z&end=2018-01-25T00:00:00.000Z&step=60s

        example: until now range query
            query=http_requests_total&start=2018-01-20T00:00:00.000Z&step=60s
            query=http_requests_total&start=2018-01-20T00:00:00.000Z&end=now&step=60s
        """

        base_url = self.configuration["url"]
        columns = [
            {"friendly_name": "timestamp", "type": TYPE_DATETIME, "name": "timestamp"},
            {"friendly_name": "value", "type": TYPE_STRING, "name": "value"},
        ]

        try:
            error = None
            query = query.strip()
            # for backward compatibility
            query = (
                "query={}".format(query) if not query.startswith("query=") else query
            )

            payload = parse_qs(query)
            query_type = "query_range" if "step" in payload.keys() else "query"

            # for the range of until now
            if query_type == "query_range" and (
                "end" not in payload.keys() or "now" in payload["end"]
            ):
                date_now = datetime.now()
                payload.update({"end": [date_now]})

            convert_query_range(payload)

            api_endpoint = base_url + "/api/v1/{}".format(query_type)
            auth, cert, verify, mtls_config = self.get_connection_auth()

            response = requests.get(api_endpoint, params=payload, auth=auth, cert=cert, verify=verify)
            response.raise_for_status()

            metrics = response.json()["data"]["result"]

            if len(metrics) == 0:
                return None, "query result is empty."

            metric_labels = metrics[0]["metric"].keys()

            for label_name in metric_labels:
                columns.append(
                    {
                        "friendly_name": label_name,
                        "type": TYPE_STRING,
                        "name": label_name,
                    }
                )

            if query_type == "query_range":
                rows = get_range_rows(metrics)
            else:
                rows = get_instant_rows(metrics)

            json_data = json_dumps({"rows": rows, "columns": columns})

        except requests.RequestException as e:
            return None, str(e)
        finally:
            _cleanup_mtls_certs(mtls_config)

        return json_data, error


register(Prometheus)
