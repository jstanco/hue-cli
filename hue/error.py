
class HueError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

__all__ = ['HueError']
