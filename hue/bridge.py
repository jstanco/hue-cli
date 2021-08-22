from typing import Iterable, Optional, Type, TypeVar

from hue.controllable import Controllable
from hue.client import HueClient
from hue.light import Light
from hue.config import Config, get_config

_T = TypeVar("_T", bound=Controllable)


class Bridge:
    def __init__(self, config: Optional[Config] = None):
        if config is None:
            config = get_config()
        self._client = HueClient(config)

    @property
    def lights(self) -> Iterable[Light]:
        """Retrieves a list of all lights on network"""
        return self._get_controllables(Light)

    def light(self, index: int) -> Light:
        """Retrieves a list of all lights on network"""
        return self._get_controllable(Light, index)

    def controllables(self, cls: Type[_T]) -> Iterable[_T]:
        """Retrieves a list of all items of class 'cls'"""
        return self._get_controllables(cls)

    def controllable(self, cls: Type[_T], index: int) -> _T:
        """Retrieves a list of all items of class 'cls'"""
        return self._get_controllable(cls, index)

    def _get_controllable(self, cls: Type[_T], index: int) -> _T:
        """Retrieves controllable of type _T at 'index'"""
        extension = "{}/{}".format(cls.class_extension, index)
        # Poll to ensure that controllable at index exists
        self._client.get(extension=extension)
        return cls(self._client, index)

    def _get_controllables(self, cls: Type[_T]) -> Iterable[_T]:
        """Retrieves a list of all items of class 'cls'"""
        response = self._client.get(extension=cls.class_extension)
        items = (cls(self._client, index=int(name)) for name in response)
        return sorted(items, key=lambda item: item.index)
