from hue.controllable import Controllable
from hue.descriptor import remote


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
