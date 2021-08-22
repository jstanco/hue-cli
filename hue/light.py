from hue.controllable import Controllable
from hue.descriptor import remote
from hue.utils import classproperty


class Light(Controllable, extension="lights"):
    @remote(attribute="on", subpath="state")
    def on(self) -> bool:
        pass

    @remote(attribute="hue", subpath="state")
    def hue(self) -> int:
        pass

    @remote(attribute="sat", subpath="state")
    def sat(self) -> int:
        pass

    @remote(attribute="bri", subpath="state")
    def bri(self) -> int:
        pass

    @remote(subpath="state")
    def state(self) -> dict:
        pass

    @remote(subpath="config")
    def config(self) -> dict:
        pass

    def switch(self) -> None:
        self.on = not self.on

    @classproperty
    def max_hue(self) -> int:
        return 2 ** 16 - 1

    @classproperty
    def max_sat(self) -> int:
        return 2 ** 8 - 2

    @classproperty
    def max_bri(self) -> int:
        return 2 ** 8 - 2
