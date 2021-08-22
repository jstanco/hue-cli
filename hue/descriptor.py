from functools import partial
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from hue.controllable import Controllable


_T = TypeVar("_T", bound=Controllable)


class _RemoteDescriptor:
    def __init__(self, func: Callable, attribute: Optional[str]) -> None:
        self._func = func
        self._attribute = attribute

    def __set_name__(self, owner, name: str) -> None:
        self._name = name

    def __get__(self, instance: _T, cls: Type[_T]) -> Any:
        response = instance.client.get(extension=instance.extension)
        return self._access(response)

    def __set__(self, instance: _T, value: Any):
        extension = "{}/state".format(instance.extension)
        if self._attribute is None:
            return instance.client.put(extension=extension, data=value)
        else:
            data = {self._attribute: value}
            return instance.client.put(extension=extension, data=data)

    def _access(self, response: Dict) -> Any:
        if self._attribute is None:
            return response["state"]
        return response["state"][self._attribute]


def remote(func: Optional[Callable] = None, *, attribute: Optional[str] = None):
    if func is None:
        return partial(remote, attribute=attribute)

    return _RemoteDescriptor(func, attribute)
