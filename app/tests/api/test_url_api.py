import schemathesis
from schemathesis.checks import not_a_server_error

from app.common.config import config

schemathesis.experimental.OPEN_API_3_1.enable()
schema = schemathesis.from_uri(f"{config.SERVER_HOST}openapi.json")


@schema.parametrize()
def test_url_shortener_endpoints(case):
    case.call_and_validate(checks=(not_a_server_error,))
