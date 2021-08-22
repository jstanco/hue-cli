import urllib.request
import json

from typing import Any, Dict, List, Optional, Union

import hue.utils as U
from hue.config import Config


class ClientRequestError(Exception):
    def __init__(self, type: str, address: str, description: str):
        super().__init__(description)
        self._type = type
        self._address = address


class HueClient:
    def __init__(self, config: Config) -> None:
        self._url: str = U.make_url(config.address, config.username)

    def request(
        self,
        extension: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        method: Optional[str] = None,
    ) -> Dict:
        url = self._create_url(extension)
        if data is not None:
            json_data = json.dumps(data).encode("utf-8")
            request = urllib.request.Request(url, data=json_data, method=method)
        else:
            request = urllib.request.Request(url, method=method)

        response = urllib.request.urlopen(request)
        response = json.loads(response.read().decode("utf-8"))
        self._validate_response(response)
        return response

    def get(
        self,
        extension: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        return self.request(extension, data, method="GET")

    def put(
        self,
        extension: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        return self.request(extension, data, method="PUT")

    def _create_url(self, extension: Optional[str] = None) -> str:
        return "{}/{}".format(self._url, extension or "")

    def _validate_response(self, response: Union[List, Dict]) -> None:
        if isinstance(response, list):
            (obj,) = response
            error = obj.get("error")
            if error is not None:
                raise ClientRequestError(**error)
