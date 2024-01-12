from redash.query_runner import BaseQueryRunner, register
import logging
import enum as e

logger = logging.getLogger(__name__)


class OAuthConnectorDSType(e.Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    INTERCOM = "intercom"
    OUTREACH = "outreach"
    GAINSIGHT = "gainsight"


class OAuthConnectorDS(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(OAuthConnectorDS, self).__init__(configuration)
        self.syntax = "custom"

    @classmethod
    def enabled(cls):
        return True

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {"refresh_token": {"type": "string", "title": "Refresh Token"}},
            "order": ["refresh_token"],
            "required": ["refresh_token"],
            "secret": ["refresh_token"],
        }

    def test_connection(self):
        return

    def run_query(self, query, user):
        raise Exception(f"No support for {query} in LiveopsOAuthDatasource query runner")
        return None, None


class Salesforce(OAuthConnectorDS):
    @classmethod
    def type(cls):
        return OAuthConnectorDSType.SALESFORCE.value


class Hubspot(OAuthConnectorDS):
    @classmethod
    def type(cls):
        return OAuthConnectorDSType.HUBSPOT.value


class Intercom(OAuthConnectorDS):
    @classmethod
    def type(cls):
        return OAuthConnectorDSType.INTERCOM.value


class Outreach(OAuthConnectorDS):
    @classmethod
    def type(cls):
        return OAuthConnectorDSType.OUTREACH.value


class Gainsight(OAuthConnectorDS):
    @classmethod
    def type(cls):
        return OAuthConnectorDSType.GAINSIGHT.value


register(Salesforce)
register(Hubspot)
register(Intercom)
register(Outreach)
register(Gainsight)
