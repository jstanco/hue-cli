import random
import sys
import argparse

from typing import Optional

import hue


def _linspace(lo, hi, n):
    dx = (hi - lo) / max(n - 1, 1)
    return [lo + i * dx for i in range(n)]


def _hue_range(mid, n, theta=50):
    lo = mid - theta / 2
    hi = mid + theta / 2
    return _linspace(lo, hi, n)


class HelpParser(argparse.ArgumentParser):
    def error(self, message):
        print("error {}".format(message), file=sys.stderr)
        self.print_help()
        sys.exit(2)


class HueCLI:
    def __init__(self):
        self._config: Optional[hue.Config] = None

    def create_parser(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(parser_class=HelpParser)

        # Create command to configure credentials
        config = subparsers.add_parser(
            "config", help="configure hue bridge credentials"
        )
        config.set_defaults(callback=self.configure)

        # Create command to set state of resources
        """
        setter = subparsers.add_parser('set',
            help='set state of hue resources')
        setter.add_argument('resource',
            help='specify resource to modify state of (lights, groups, etc)')
        setter.set_defaults(callback=self.set_resource)
        """

        # TODO use lights to add range of acceptable choices
        switch = subparsers.add_parser("switch", help="switch lights on/off")
        switch.add_argument(
            "value",
            default=None,
            nargs="?",
            type=str,
            choices=["on", "off", None],
            help="Override existing on/off value",
        )
        switch.add_argument(
            "-i", "--index", type=int, help="Specific light index to modify"
        )
        switch.set_defaults(callback=self.switch)

        # Create command to set light color
        color = subparsers.add_parser("color")
        color.add_argument("--hue", type=float, help="hue value to set")
        color.add_argument(
            "--sat", type=float, default=100, help="saturation value to set"
        )
        color.add_argument(
            "--bri", type=float, default=75, help="brightness value to set"
        )
        color.add_argument(
            "-i", "--index", type=int, help="Specific light index to modify"
        )
        color.set_defaults(callback=self.color)

        hrange = subparsers.add_parser("range")
        hrange.add_argument("--hue", type=float, help="hue value to set")
        hrange.add_argument(
            "--sat", type=float, default=100, help="saturation value to set"
        )
        hrange.add_argument(
            "--bri", type=float, default=75, help="brightness value to set"
        )
        hrange.set_defaults(callback=self.hrange)
        return parser

    def configure(self, args):
        devices = hue.find_available_devices()
        if not devices:
            print(
                "No available hue devices found on network, exiting.",
                file=sys.stderr,
            )
            sys.exit(2)
        print("Found {} Hue device(s)".format(len(devices)))
        for i, (_, address) in enumerate(devices):
            print("{})".format(i + 1), address)

        try:
            _, address = devices[self._get_input_index()]
        except IndexError as e:
            print("{}, exiting".format(e), file=sys.stderr)
            sys.exit(2)
        else:
            passkey = input("Enter device passkey: ").strip()
            self._config = hue.Config(address, passkey)
            self._config.write()
            print("Configuration successfully written!")
            return 0

    def switch(self, args):
        self._setup_config(args)
        bridge = hue.Bridge(self._config.address, self._config.username)

        if args.index is not None:
            lights = [bridge.light(args.index)]
        else:
            lights = bridge.lights

        if args.value is None:
            for light in lights:
                light.switch()
        elif args.value.lower() == "on":
            for light in lights:
                light.on = True
        elif args.value.lower() == "off":
            for light in lights:
                light.on = False
        return 0

    def color(self, args):
        self._setup_config(args)
        bridge = hue.Bridge(self._config.address, self._config.username)
        lights = bridge.lights

        if args.index is not None:
            lights = [bridge.light(args.index)]
        else:
            lights = bridge.lights

        for light in lights:
            if args.hue is None:
                # Set random hue value
                hueval = random.random() * 360
            else:
                hueval = args.hue
            light.hue = int(hueval / 360 * light.max_hue) % light.max_hue
            light.sat = int(args.sat / 100 * light.max_sat)
            light.bri = int(args.bri / 100 * light.max_bri)
        return 0

    def hrange(self, args):
        self._setup_config(args)
        bridge = hue.Bridge(self._config.address, self._config.username)
        lights = bridge.lights

        if args.hue is None:
            # Set random hue value
            hueval = random.random() * 360
        else:
            hueval = args.hue

        # Generate range of colors
        for h, light in zip(_hue_range(hueval, len(lights)), lights):
            light.hue = int(h / 360 * light.max_hue) % light.max_hue
            light.sat = int(args.sat / 100 * light.max_sat)
            light.bri = int(args.bri / 100 * light.max_bri)
        return 0

    def _setup_config(self, args):
        try:
            self._config = hue.Config.from_file()
        except FileNotFoundError:
            self.configure(args)

    def _get_input_index(self):
        index = int(input("Please select one: "))
        if index < 1:
            raise IndexError("Index must be greater than zero")
        return index - 1


def main():
    cli = HueCLI()
    parser = cli.create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 2

    args = parser.parse_args()
    return args.callback(args)


if __name__ == "__main__":
    main()
