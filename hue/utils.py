from typing import Any, Callable, Type, TypeVar


_T = TypeVar("_T")


class classproperty:
    def __init__(self, fget: Callable) -> None:
        self._fget = fget

    def __get__(self, instance: _T, cls: Type[_T]) -> Any:
        return self._fget(cls)


def make_url(address: str, username: str) -> str:
    return "http://{}/api/{}".format(address, username)
