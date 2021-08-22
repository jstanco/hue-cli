from typing import Any, Dict, Optional, TypeVar

from hue.utils import classproperty
from hue.client import HueClient


_T = TypeVar("_T", bound="Controllable")


class Controllable:
    _cls_extension = ""

    def __init_subclass__(
        cls, /, extension: str, **kwargs: Dict[str, Any]
    ) -> None:
        cls._cls_extension = extension
        super().__init_subclass__(**kwargs)  # type: ignore[call-arg]

    def __init__(self, client: HueClient, index: int) -> None:
        self._client = client
        self._index = index
        self._extension: str = self._make_extension(index)

    @classproperty
    def class_extension(cls) -> str:
        return cls._cls_extension

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def index(self) -> int:
        return self._index

    @property
    def client(self) -> HueClient:
        return self._client

    def _make_extension(self, index: int) -> str:
        return "{}/{}".format(self._cls_extension, index)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return "<{}[{}]>".format(cls, self._index)
