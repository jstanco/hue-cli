import configparser
import logging
import os

from typing import Optional, Type, TypeVar

import hue.utils as U


_logger = logging.getLogger(__name__)
_T = TypeVar("_T", bound="Config")


class ConfigNotFoundError(Exception):
    pass


class Config:
    _CREDENTIALS_PATH = ".hue"

    def __init__(self, address: str, username: str) -> None:
        self._address = address
        self._username = username
        self._url: str = U.make_url(address, username)

    @property
    def username(self) -> str:
        return self._username

    @property
    def address(self) -> str:
        return self._address

    @property
    def url(self) -> str:
        return self._url

    def write(self) -> None:
        config = configparser.ConfigParser()
        config["default"] = {"ipaddr": self._address, "passkey": self._username}
        path = self._make_credentials_path()
        _logger.debug("Writing config to default user path {}".format(path))
        with open(path, "w") as file:
            config.write(file)

    @classmethod
    def from_file(cls: Type[_T]) -> _T:
        config = configparser.ConfigParser()
        path = cls._make_credentials_path()
        _logger.debug("Loading config from default user path {}".format(path))
        if not os.path.exists(path):
            raise ConfigNotFoundError(
                "Could not locate hue configuration file on disk"
            )
        config.read(path)
        address = config["default"]["ipaddr"]
        username = config["default"]["passkey"]
        return cls(address, username)

    @classmethod
    def _make_credentials_path(cls) -> str:
        return os.path.join(os.path.expanduser("~"), cls._CREDENTIALS_PATH)


_CONFIG: Optional[Config] = None


def get_config() -> Config:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = Config.from_file()
        _logger.debug("Default config successfully loaded")
    return _CONFIG


def set_config(config: Config) -> None:
    global _CONFIG
    _CONFIG = config
    _logger.debug("Hue config set")
