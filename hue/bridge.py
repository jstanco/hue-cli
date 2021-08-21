import urllib.request
import json

from hue.light import Light
from hue.error import HueError


class NetworkComponent:
    def __init__(self, address: str, username, *args):
        self._ip_address = address
        self._username = username
        self._update_url()

    def _update_url(self):
        self.url = f"http://{self._ip_address}/api/{self._username}"

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self._update_url()

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value
        self._update_url()

    def _validate_response(self, response):
        for obj in response:
            if isinstance(obj, dict):
                error = obj.get("error")
                if error is not None:
                    raise HueError(error)

    def request(self, ext=None, data=None, **kwargs):
        url = "{}/{}".format(self.url, ext or "")
        if data is not None:
            data = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url, data=data, **kwargs)
        response = urllib.request.urlopen(request)
        response = json.loads(response.read().decode("utf-8"))
        self._validate_response(response)
        return response

    def _get_controllables(self, cls):
        """Retrieves a list of all items of class"""
        response = self.request(ext=cls.extension(), method="GET")
        items = (cls(self, name, **value) for name, value in response.items())
        return sorted(items, key=lambda item: item.id)


class Bridge(NetworkComponent):
    def __init__(self, ip_address, username):
        super().__init__(ip_address, username)

    @property
    def lights(self):
        """Retrieves a list of all lights on network"""
        return self._get_controllables(cls=Light)


__all__ = ["Bridge"]
