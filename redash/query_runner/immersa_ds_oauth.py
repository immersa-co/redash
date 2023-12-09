from redash.query_runner import BaseQueryRunner, register
import logging
import enum as e

logger = logging.getLogger(__name__)


class LOOAuthConnectorDSType(e.Enum):
    SALESFORCE = "lo_salesforce"
    HUBSPOT = "lo_hubspot"
    INTERCOM = "lo_intercom"
    OUTREACH = "lo_outreach"
    GAINSIGHT = "lo_gainsight"


class LiveopsOAuthDatasource(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(LiveopsOAuthDatasource, self).__init__(configuration)
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


class LOSalesforce(LiveopsOAuthDatasource):
    @classmethod
    def name(cls):
        return "LOSalesforce"

    @classmethod
    def type(cls):
        return LOOAuthConnectorDSType.SALESFORCE.value


class LOHubspot(LiveopsOAuthDatasource):
    @classmethod
    def name(cls):
        return "LOHubspot"

    @classmethod
    def type(cls):
        return LOOAuthConnectorDSType.HUBSPOT.value


class LOIntercom(LiveopsOAuthDatasource):
    @classmethod
    def name(cls):
        return "LOIntercom"

    @classmethod
    def type(cls):
        return LOOAuthConnectorDSType.INTERCOM.value


class LOOutreach(LiveopsOAuthDatasource):
    @classmethod
    def name(cls):
        return "LOOutreach"

    @classmethod
    def type(cls):
        return LOOAuthConnectorDSType.OUTREACH.value


class LOGainsight(LiveopsOAuthDatasource):
    @classmethod
    def name(cls):
        return "LOGainsight"

    @classmethod
    def type(cls):
        return LOOAuthConnectorDSType.GAINSIGHT.value


register(LOSalesforce)
register(LOHubspot)
register(LOIntercom)
register(LOOutreach)
register(LOGainsight)
