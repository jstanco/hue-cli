from hue.controllable import Controllable


class Light(Controllable):
    EXT = "lights"

    max_hue = 2 ** 16 - 1
    max_sat = 2 ** 8 - 2
    max_bri = 2 ** 8 - 2

    def __init__(self, bridge, idnum, **kwargs):
        super().__init__(bridge, idnum, **kwargs)


__all__ = ["Light"]
