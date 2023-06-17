from redash.query_runner import BaseQueryRunner, register
import logging

logger = logging.getLogger(__name__)

class S3(BaseQueryRunner):
    should_annotate_query = False

    def __init__(self, configuration):
        super(S3, self).__init__(configuration)
        self.syntax = "custom"

    @classmethod
    def name(cls):
        return "AWS S3"

    @classmethod
    def type(cls):
        return "s3"

    @classmethod
    def enabled(cls):
        return True

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "bucket": {"type": "string", "title": "Bucket Path"},
                "key_id": {"type": "string", "title": "Access Key ID"},
                "key_secret": {"type": "string", "title": "Access Key Secret"},
            },
            "order": ["bucket", "key_id", "key_secret"],
            "required": ["bucket", "key_id", "key_secret"],
            "secret": ["key_secret"],
        }

    def test_connection(self):
        return

    def run_query(self, query, user):
        raise Exception(f"No support for {query} in S3 query runner")
        return None, None

register(S3)

