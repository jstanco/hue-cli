class BaseControllable:

    def __init__(self, bridge):
        self.bridge = bridge

    def _update(self, state):
        self.state.update(state)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value


class Controllable(BaseControllable):
    EXT = None

    def __init__(self, bridge, idnum, **kwargs):
        self.__dict__.update(**kwargs)
        super().__init__(bridge)
        self.id = idnum
        self.ext = f'{self.EXT}/{self.id}'

    def _request(self, data=None, ext=None, **kwargs):
        ext = '/'.join((self.ext, ext or ''))
        return self.bridge.request(data=data, ext=ext, **kwargs)

    def __setattr__(self, name, value):
        state = super().__getattr__('state')
        if name == 'state':
            self._request(data=value, ext='state', method='PUT')
            self._update(value)
        if name in state:
            data = {name: value}
            self._request(data=data, ext='state', method='PUT')
            self._update(data)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name == 'state':
            response = self._request(method='GET')
            return response['state']
        if name in super().__getattr__('state'):
            response = self._request(method='GET')
            return response['state'][name]
        else:
            return super().__getattr__(name)
