import json
import os
from types import SimpleNamespace
from typing import AnyStr
from typing import Union

import requests
from dotenv import load_dotenv

from highway.utils import clean_html


load_dotenv()

# Highway Integration variables
HIGHWAY_URL = os.getenv("HIGHWAY_URL", default=None)
HIGHWAY_PRIVATE_KEY = os.getenv("HIGHWAY_PRIVATE_KEY", default=None)
HIGHWAY_TIMEOUT = 15


class HighwayError(Exception):
    def __init__(self, error_json):
        super(HighwayError, self).__init__(error_json)
        self.error_json = error_json


class MalformedRequestError(HighwayError):
    pass


class AuthenticationError(HighwayError):
    pass


class ProcessingError(HighwayError):
    pass


class ResourceNotFoundError(HighwayError):
    pass


class ParameterValidationError(HighwayError):
    pass


class ApiError(HighwayError):
    pass


class HighwayApi:
    """
    Build request to highway API
    """

    params = {}
    headers = {}
    to_dict = {}

    def __init__(self, base_url=HIGHWAY_URL):
        self.base_url = base_url
        self.params["private_key"] = HIGHWAY_PRIVATE_KEY

    def to_object(self, response: dict):
        self.to_dict = response
        return SimpleNamespace(**response)

    def build_http_request(self, request, model, payload: dict = None):
        return request(
            url=f"{self.base_url}/{model}",
            json=payload,
            params=self.params,
            headers=self.headers,
        )

    def manage_errors(self, result: Union[dict, str], **kwargs):
        """
        If there is an error sending the request and return a bad
        json response try to convert to json error message
        :param result:
        :param kwargs:
        :return:
        """
        if not isinstance(result, dict):
            text = clean_html(str(result))
            error = {"message": text}
        else:
            error = result
        status_code = kwargs.get("status_code", -1)
        if status_code == 400:
            raise MalformedRequestError(error)
        elif status_code == 401:
            raise AuthenticationError(error)
        elif status_code == 404:
            raise ResourceNotFoundError(error)
        elif status_code == 500:
            raise ApiError(error)
        else:
            raise HighwayError(error)

    def send_request(self, request_function, method, **kwargs):
        try:
            response = request_function(timeout=HIGHWAY_TIMEOUT, **kwargs)
            status_code = response.status_code
            try:
                result = response.json()
            except json.decoder.JSONDecodeError:
                result = response.content
                if not result:
                    result = {}
        except (Exception, SystemExit) as e:
            result = e
            response = None
            status_code = None

        if not response or not isinstance(result, dict):
            kwargs.update({"method": method, "status_code": status_code})
            self.manage_errors(result, **kwargs)
        return result

    def send_post_request(self, **kwargs):
        return self.send_request(requests.post, "POST", **kwargs)

    def send_delete_request(self, **kwargs):
        return self.send_request(requests.delete, "DELETE", **kwargs)

    def send_get_request(self, **kwargs):
        return self.send_request(requests.get, "GET", **kwargs)

    def send_patch_request(self, **kwargs):
        return self.send_request(requests.patch, "PATCH", **kwargs)

    def send_put_request(self, **kwargs):
        return self.send_request(requests.put, "PUT", **kwargs)


class HighwayModel:
    api = HighwayApi()
    name: str

    @classmethod
    def update(cls, oid: AnyStr, data: dict):
        result = cls.api.build_http_request(
            cls.api.send_put_request, model=f"{cls.name}/{oid}", payload=data
        )
        return cls.api.to_object(result)

    @classmethod
    def retrieve(cls, oid: AnyStr):
        result = cls.api.build_http_request(
            cls.api.send_get_request, model=f"{cls.name}/{oid}"
        )
        return cls.api.to_object(result)


class Project(HighwayModel):
    name = "project"


class Plan(HighwayModel):
    name = "plan"


class Service(HighwayModel):
    name = "service"


class Client(HighwayModel):
    name = "client"


class Route(HighwayModel):
    name = "route"
