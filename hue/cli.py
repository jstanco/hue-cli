import json
import random
import pprint
import sys
import hue
import configparser
import os
from urllib import request
import ssl
import argparse


def _linspace(lo, hi, n):
    dx = (hi - lo) / max(n - 1, 1)
    return [lo + i * dx for i in range(n)]


def _hue_range(mid, n, theta=90):
    lo = mid - theta / 2
    hi = mid + theta / 2
    return _linspace(lo, hi, n)


class HelpParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('error {}\n'.format(message))
        self.print_help()
        sys.exit(2)


class HueCLI:

    _discovery_url = 'https://discovery.meethue.com/'

    def __init__(self):
        self.ipaddr = None
        self.passkey = None

    @staticmethod
    def _find_credentials_path():
        return os.path.join(os.path.expanduser('~'), '.hue')    

    @staticmethod
    def _find_available_devices():
        sctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        response = request.urlopen(HueCLI._discovery_url, context=sctx)
        return json.loads(response.read().decode('utf-8'))

    @staticmethod
    def _setup_credentials(ipaddr, passkey):
        config = configparser.ConfigParser()
        config['default'] = {
            'ipaddr': ipaddr,
            'passkey': passkey
        }
        path = HueCLI._find_credentials_path()
        with open(path, 'w') as f:
            config.write(f)
        print('Configuration written to \'{}\''.format(path))        

    def _find_credentials(self, args):
        path = self._find_credentials_path()
        if not os.path.exists(path):
            self.configure(args)

        config = configparser.ConfigParser()
        config.read(self._find_credentials_path())
        default = config['default']
        self.ipaddr = default['ipaddr']
        self.passkey = default['passkey']
        return 0

    def _filter_device_index(self, index):
        index = int(index) - 1
        if index < 0:
            raise ValueError
        return index

    def create_parser(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(parser_class=HelpParser)

        # Create command to configure credentials
        config = subparsers.add_parser('config',
            help='configure hue bridge credentials') 
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
        switch = subparsers.add_parser('switch',
            help='switch lights on/off')
        switch.add_argument('value', default=None, nargs='?', type=str,
            choices=['on', 'off', None],
            help='Override existing on/off value')
        switch.add_argument('-i', '--index', type=int,
            help='Specific light index to modify')
        switch.set_defaults(callback=self.switch)

        # Create command to set light color
        color = subparsers.add_parser('color')
        color.add_argument('--hue', type=float,
            help='hue value to set')
        color.add_argument('--sat', type=float,
            default=100,
            help='saturation value to set')
        color.add_argument('--bri', type=float,
            default=75,
            help='brightness value to set')
        color.add_argument('-i', '--index', type=int,
            help='Specific light index to modify')
        color.set_defaults(callback=self.color)

        hrange = subparsers.add_parser('range')
        hrange.add_argument('--hue', type=float,
            help='hue value to set')
        hrange.add_argument('--sat', type=float,
            default=100,
            help='saturation value to set')
        hrange.add_argument('--bri', type=float,
            default=75,
            help='brightness value to set')
        hrange.set_defaults(callback=self.hrange)
        return parser

    def configure(self, args):
        devices = self._find_available_devices()
        if not devices:
            sys.stderr.write('No available hue devices found on network, exiting.\n')
            sys.exit(2)
        print('Found {} Hue device(s)'.format(len(devices)))
        for i, device in enumerate(devices):
            print('{})'.format(i + 1), device['internalipaddress'])

        try:
            index = input('Please select one: ')
            device = devices[self._filter_device_index(index)]
            ipaddr = device['internalipaddress']
        except ValueError:
            sys.stderr.write('Invalid device index, exiting.\n')
        except IndexError:
            sys.stderr.write('Device index out of range, exiting.\n')
            sys.exit(2)

        passkey = input('Enter device passkey: ').strip()
        self._setup_credentials(ipaddr, passkey)
        self.ipaddr = ipaddr
        self.passkey = passkey
        return 0

    def switch(self, args):
        self._find_credentials(args)
        bridge = hue.Bridge(self.ipaddr, self.passkey)
        lights = bridge.lights
        
        if args.index is not None:
            lights = [lights[args.index - 1]]
        
        if args.value is None:
            states = [light.on for light in lights]
            for light, state in zip(lights, states):
                light.on = not state
        elif args.value.lower() == 'on':
            for light in lights:
                light.on = True
        elif args.value.lower() == 'off':
            for light in lights:
                light.on = False
        return 0

    def color(self, args):
        self._find_credentials(args)
        bridge = hue.Bridge(self.ipaddr, self.passkey)
        lights = bridge.lights

        if args.index is not None:
            lights = [lights[args.index - 1]]

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
        self._find_credentials(args)
        bridge = hue.Bridge(self.ipaddr, self.passkey)
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


def main():
    cli = HueCLI()
    parser = cli.create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 2

    args = parser.parse_args()
    return args.callback(args)


if __name__ == '__main__':
    main()
