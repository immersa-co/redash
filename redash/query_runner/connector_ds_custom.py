import enum as e
import logging

from redash.query_runner import BaseQueryRunner, register

logger = logging.getLogger(__name__)


class ConnectorDSType(e.Enum):
    AMPLITUDE = "amplitude"
    MIXPANEL = "mixpanel"
    PENDO = "pendo"
    MARKETO = "marketo"
    FULLSTORY = "fullstory"
    ANALYTICS_WORKSPACE = "analytics_workspace"
    CHARGEBEE = "chargebee"


class ConnectorDS(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(ConnectorDS, self).__init__(configuration)
        self.syntax = "custom"

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "title": "API Token"},
            },
            "order": ["api_key"],
            "required": ["api_key"],
            "secret": ["api_key"],
        }

    @classmethod
    def enabled(cls):
        return True

    def test_connection(self):
        return

    def run_query(self, query, user):
        raise Exception(f"No support for {query} in ConnectorDS query runner")
        return None, None


class Marketo(ConnectorDS):
    # Marketo Client Key, Secret, SOAP API Encryption Key, Base URL
    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "title": "Client API Key"},
                "api_secret": {"type": "string", "title": "Client API Secret"},
                "soap_api_encryption_key": {"type": "string", "title": "Soap API Encryption Key"},
                "soap_api_user_id": {"type": "string", "title": "Soap API User Id"},
                "base_url": {"type": "string", "title": "Base URL"},
                "identity_endpoint": {"type": "string", "title": "Identity Endpoint"},
                "rest_endpoint": {"type": "string", "title": "Rest Endpoint"},
                "soap_endpoint": {"type": "string", "title": "Soap Endpoint"},
            },
            "order": [
                "api_key",
                "api_secret",
                "soap_api_encryption_key",
                "soap_api_user_id",
                "base_url",
                "identity_endpoint",
                "rest_endpoint",
                "soap_endpoint",
            ],
            "required": [
                "api_key",
                "api_secret",
                "soap_api_encryption_key",
                "soap_api_user_id",
                "base_url",
            ],
            "secret": ["api_key", "api_secret", "soap_api_encryption_key"],
        }

    @classmethod
    def type(cls):
        return ConnectorDSType.MARKETO.value


class Amplitude(ConnectorDS):
    @classmethod
    def configuration_schema(cls):
        # Amplitude - api key/secret
        return {
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "title": "API Key"},
                "api_secret": {"type": "string", "title": "Secret"},
            },
            "order": ["api_key", "api_secret"],
            "required": ["api_key", "api_secret"],
            "secret": ["api_key", "api_secret"],
        }

    @classmethod
    def type(cls):
        return ConnectorDSType.AMPLITUDE.value


class Pendo(ConnectorDS):
    @classmethod
    def type(cls):
        return ConnectorDSType.PENDO.value


class Mixpanel(ConnectorDS):
    @classmethod
    def type(cls):
        return ConnectorDSType.MIXPANEL.value


class Fullstory(ConnectorDS):
    @classmethod
    def type(cls):
        return ConnectorDSType.FULLSTORY.value


class AnalyticsWorkspace(ConnectorDS):
    @classmethod
    def type(cls):
        return ConnectorDSType.ANALYTICS_WORKSPACE.value


class Chargebee(ConnectorDS):
    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "title": "API Token"},
                "crm_base_url": {"type": "string", "title": "CRM Base URL"}
            },
            "order": ["api_key", "crm_base_url"],
            "required": ["api_key", "crm_base_url"],
            "secret": ["api_key", "crm_base_url"],
        }

    @classmethod
    def type(cls):
        return ConnectorDSType.CHARGEBEE.value


register(Marketo)
register(Amplitude)
register(Pendo)
register(Mixpanel)
register(Fullstory)
register(AnalyticsWorkspace)
register(Chargebee)
