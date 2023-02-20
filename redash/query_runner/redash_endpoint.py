import time, requests, json, logging
from redash.query_runner import BaseQueryRunner, register

logger = logging.getLogger(__name__)

_PENDING, _STARTED, _SUCCESS, _FAILURE, _CANCELLED = 1, 2, 3, 4, 5

class RedashEndpoint(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(RedashEndpoint, self).__init__(configuration)
        self.syntax = "json"

    @classmethod
    def name(cls):
        return "Redash Endpoint"

    @classmethod
    def type(cls):
        return "redash_endpoint"

    @classmethod
    def enabled(cls):
        return True

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "title": "Redash URL"},
                "api_key": {"type": "string", "title": "User API Key"},
            },
            "order": ["url", "api_key"],
            "required": ["url", "api_key"],
            "secret": ["api_key"],
        }

    def test_connection(self):
        return

    def run_query(self, query, user):
        logger.debug("RedashEndpoint is about to execute query: %s", query)

        url = f"{self.configuration['url']}/api"
        headers = {"Authorization": f"Key {self.configuration['api_key']}"}

        manifest = json.loads(query)
        qid = manifest['query_id']
        if 'params' in manifest:
            payload = {"max_age": manifest.get('max_age', 0), "parameters": manifest['params']}
        else:
            payload = {"max_age": manifest.get('max_age', 0)}

        response = requests.request("POST", f"{url}/queries/{qid}/results", headers=headers, json=payload)
        if 'job' in response.json():
            job = response.json()['job']
            poll = f"{url}/queries/{qid}/jobs/{job['id']}"
            timeout = int(time.time()) + manifest.get('timeout_minutes', 5) * 60
            delay, backoff = 1, 2
            while job.get('status', None) != _SUCCESS:
                if int(time.time()) >= timeout:
                    requests.request("DELETE", poll, headers=headers)
                    raise Exception(f"Redash Endpoint: TIMEOUT {poll}")
                time.sleep(delay)
                delay *= backoff if delay < 30 else 30

                job = requests.request("GET", poll, headers=headers).json()["job"]
                if job['status'] == _FAILURE:
                    raise Exception(f"Redash Endpoint: {job['error']} FAILURE {poll}")
                if job['status'] == _CANCELLED:
                    raise Exception(f"Redash Endpoint: CANCELLED {poll}")
            result = job['query_result_id']
        else:
            result = response.json()['query_result']['id']
        logger.info(f"Query result Id: {result}")

        raw_data = b""
        response = requests.get(f"{url}/query_results/{result}", headers=headers, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            raw_data += chunk

        result_json = json.loads(raw_data.decode("utf-8"))
        result_data = result_json['query_result'].get('data')
        return json.dumps(result_data), None


register(RedashEndpoint)

