from functools import partial
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from hue.controllable import Controllable


_T = TypeVar("_T", bound=Controllable)


class _RemoteAttributeDescriptor:
    def __init__(
        self, func: Callable, attribute: str, subpath: str = "state"
    ) -> None:
        self._func = func
        self._attribute = attribute
        self._subpath = subpath

    def __set__(self, instance: _T, value: Any) -> None:
        extension = "{}/{}".format(instance.extension, self._subpath)
        data = {self._attribute: value}
        instance.client.put(extension=extension, data=data)

    def __get__(self, instance: _T, cls: Type[_T]) -> Any:
        response = instance.client.get(extension=instance.extension)
        return response[self._subpath][self._attribute]


class _RemoteStateDescriptor:
    def __init__(self, func: Callable, subpath: str = "state") -> None:
        self._func = func
        self._subpath = subpath

    def __set__(self, instance: _T, value: Any) -> None:
        extension = "{}/{}".format(instance.extension, self._subpath)
        instance.client.put(extension=extension, data=value)

    def __get__(self, instance: _T, cls: Type[_T]) -> Any:
        response = instance.client.get(extension=instance.extension)
        return response[self._subpath]


def _remoteattr(
    func: Optional[Callable] = None,
    *,
    attribute: Optional[str] = None,
    subpath: str = "state"
):
    if func is None:
        return partial(_remoteattr, attribute=attribute, subpath=subpath)

    return _RemoteAttributeDescriptor(func, attribute, subpath)


def _remotestate(func: Optional[Callable] = None, *, subpath: str = "state"):
    if func is None:
        return partial(_remotestate, subpath=subpath)
    return _RemoteStateDescriptor(func, subpath)


def remote(
    func: Optional[Callable] = None,
    *,
    attribute: Optional[str] = None,
    subpath: str = "state"
):
    if attribute is None:
        return _remotestate(func, subpath=subpath)
    return _remoteattr(func, attribute=attribute, subpath=subpath)
