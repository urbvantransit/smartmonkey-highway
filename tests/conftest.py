import json

import pytest


@pytest.fixture
def fake_request():
    import httpretty

    httpretty.enable()
    yield httpretty
    httpretty.disable()
    httpretty.reset()


@pytest.fixture
def mock_highway_api(fake_request, mock_request):
    from highway import HighwayApi, HighwayModel, HIGHWAY_URL

    response = {"foo": "bar"}
    oid = 123
    models = ["project", "plan", "service", "client", "route"]
    http_verbs = [fake_request.GET, fake_request.PUT]
    for model in models:
        for http_verb in http_verbs:
            mock_request(
                path=f"/{model}/{oid}", response=response, req_type=http_verb
            )
    example_api = HighwayApi(base_url=HIGHWAY_URL)
    HighwayModel.api = example_api
    return HIGHWAY_URL, oid, response


@pytest.fixture
def mock_request(fake_request):
    from highway import HIGHWAY_URL

    def _register_request(
        path, response, status=200, req_type=fake_request.GET
    ):
        uri = f"{HIGHWAY_URL}{path}"
        fake_request.register_uri(
            method=req_type,
            uri=uri,
            body=json.dumps(response),
            content_type="application/json",
            status=status,
        )
        return fake_request

    return _register_request
