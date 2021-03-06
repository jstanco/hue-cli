import json
import ssl

from urllib import request

from typing import Any, Callable, List, Tuple, Type, TypeVar


_T = TypeVar("_T")
_DISCOVERY = "https://discovery.meethue.com/"


class classproperty:
    def __init__(self, fget: Callable) -> None:
        self._fget = fget

    def __get__(self, instance: _T, cls: Type[_T]) -> Any:
        return self._fget(cls)


def make_url(address: str, username: str) -> str:
    return "http://{}/api/{}".format(address, username)


def find_available_devices() -> List[Tuple[str, str]]:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    response = request.urlopen(_DISCOVERY, context=context)
    devices = json.loads(response.read().decode())
    return [(d["id"], d["internalipaddress"]) for d in devices]
