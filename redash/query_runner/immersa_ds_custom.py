from redash.query_runner import BaseQueryRunner, register
import logging
import enum as e

logger = logging.getLogger(__name__)


class LOConnectorDSType(e.Enum):
    AMPLITUDE = "lo_amplitude"
    MIXPANEL = "lo_mixpanel"
    PENDO = "lo_pendo"
    REDASH = "lo_redash"
    GOOGLESHEET = "lo_googlesheet"
    MARKETO = "lo_marketo"
    FULLSTORY = "lo_fullstory"
    ANALYTICS_WORKSPACE = "lo_analytics_workspace"


class LiveopsDatasource(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(LiveopsDatasource, self).__init__(configuration)
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
        raise Exception(f"No support for {query} in LiveopsDatasource query runner")
        return None, None


class LOMarketo(LiveopsDatasource):
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
    def name(cls):
        return "LOMarketo"

    @classmethod
    def type(cls):
        return LOConnectorDSType.MARKETO.value


class LOGoogleSheet(LiveopsDatasource):
    @classmethod
    def configuration_schema(cls):
        # GoogleSheet - Need to store Sheet Ids
        return {
            "type": "object",
            "properties": {
                "spreadsheet_id": {"type": "string", "title": "Spread Sheet Id"},
                "tab_id": {"type": "string", "title": "Tab Id"},
            },
            "order": ["spreadsheet_id", "tab_id"],
            "required": ["spreadsheet_id"],
            "secret": [],
        }

    @classmethod
    def name(cls):
        return "LOGoogleSheet"

    @classmethod
    def type(cls):
        return LOConnectorDSType.GOOGLESHEET.value


class LORedash(LiveopsDatasource):
    @classmethod
    def configuration_schema(cls):
        # Redash - URL, QueryId, APIKey
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "title": "Redash URL"},
                "query_id": {"type": "string", "title": "Query Id"},
                "api_key": {"type": "string", "title": "API Key"},
            },
            "order": ["url", "query_id", "api_key"],
            "required": ["url", "query_id", "api_key"],
            "secret": ["api_key"],
        }

    @classmethod
    def name(cls):
        return "LORedash"

    @classmethod
    def type(cls):
        return LOConnectorDSType.REDASH.value


class LOAmplitude(LiveopsDatasource):
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
    def name(cls):
        return "LOAmplitude"

    @classmethod
    def type(cls):
        return LOConnectorDSType.AMPLITUDE.value


class LOPendo(LiveopsDatasource):
    @classmethod
    def name(cls):
        return "LOPendo"

    @classmethod
    def type(cls):
        return LOConnectorDSType.PENDO.value


class LOMixpanel(LiveopsDatasource):
    @classmethod
    def name(cls):
        return "LOMixpanel"

    @classmethod
    def type(cls):
        return LOConnectorDSType.MIXPANEL.value


class LOFullstory(LiveopsDatasource):
    @classmethod
    def name(cls):
        return "LOFullStory"

    @classmethod
    def type(cls):
        return LOConnectorDSType.FULLSTORY.value


class LOAnalyticsWorkspace(LiveopsDatasource):
    @classmethod
    def name(cls):
        return "LOAnalyticsWorkspace"

    @classmethod
    def type(cls):
        return LOConnectorDSType.ANALYTICS_WORKSPACE.value


register(LOMarketo)
register(LOGoogleSheet)
register(LORedash)
register(LOAmplitude)
register(LOPendo)
register(LOMixpanel)
register(LOFullstory)
register(LOAnalyticsWorkspace)
