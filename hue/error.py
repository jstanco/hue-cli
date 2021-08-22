class HueError(Exception):
    def __init__(self, type: str, address: str, description: str):
        super().__init__(description)
        self._type = type
        self._address = address
