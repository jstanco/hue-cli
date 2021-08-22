from hue.controllable import Controllable
from hue.descriptor import remote


class Light(Controllable, extension="lights"):
    @remote(attribute="on")
    def on(self) -> bool:
        pass

    @remote(attribute="hue")
    def hue(self) -> int:
        pass

    @remote(attribute="sat")
    def sat(self) -> int:
        pass

    @remote(attribute="bri")
    def bri(self) -> int:
        pass

    @remote
    def state(self) -> dict:
        pass

    def switch(self) -> None:
        self.on = not self.on
