import pytest

from highway import ApiError
from highway import AuthenticationError
from highway import Client
from highway import HIGHWAY_URL
from highway import HighwayApi
from highway import HighwayError
from highway import MalformedRequestError
from highway import Plan
from highway import Project
from highway import ResourceNotFoundError
from highway import Route
from highway import Service


class TestHighwayModels:
    models = [Project, Plan, Service, Client, Route]

    def test_highway_get(self, mock_highway_api):
        base_url, oid, response = mock_highway_api
        for model in self.models:
            result = model.retrieve(oid)
            assert hasattr(result, "foo")
            assert getattr(result, "foo") == "bar"

    def test_highway_put(self, mock_highway_api):
        base_url, oid, response = mock_highway_api
        for model in self.models:
            updated = model.update(oid, response)
            assert hasattr(updated, "foo")
            assert getattr(updated, "foo") == "bar"


class TestHighwayApiInterface:
    api = HighwayApi()

    def test_json_response_error(self, mock_request):
        error_response = {"message": "Some error message"}
        mock_request("/plan/123", error_response, status=500)

        with pytest.raises(ApiError):
            self.api.send_get_request(url=f"{HIGHWAY_URL}/plan/123")

    def test_html_response_error(self, mock_request, fake_request):
        error_response = "<h1>Some html text error</h1>"
        mock_request(
            "/plan/123",
            error_response,
            status=503,
            req_type=fake_request.PATCH,
        )
        with pytest.raises(HighwayError):
            self.api.send_patch_request(url=f"{HIGHWAY_URL}/plan/123")

    def test_connection_error(self):
        with pytest.raises(HighwayError):
            self.api.send_patch_request(url="https://some-missing-url.test")

    def test_authentication_error(self, mock_request, fake_request):
        error_response = {"message": "Invalid API key."}
        mock_request(
            "/plan/123", error_response, status=401, req_type=fake_request.POST
        )
        with pytest.raises(AuthenticationError):
            self.api.send_post_request(url=f"{HIGHWAY_URL}/plan/123")

    def test_bad_request(self, mock_request, fake_request):
        error_response = {"message": "Bad request"}
        mock_request(
            "/plan/123",
            error_response,
            status=400,
            req_type=fake_request.DELETE,
        )
        with pytest.raises(MalformedRequestError):
            self.api.send_delete_request(url=f"{HIGHWAY_URL}/plan/123")

    def test_resource_not_found(self, mock_request, fake_request):
        error_response = {"message": "Resource not found"}
        mock_request(
            "/plan/123",
            error_response,
            status=404,
            req_type=fake_request.DELETE,
        )
        with pytest.raises(ResourceNotFoundError):
            self.api.send_delete_request(url=f"{HIGHWAY_URL}/plan/123")
