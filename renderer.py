from enum import Enum, auto

class RenderMode(Enum):
    NORMAL = 1
    UI = 2

class RenderLayer(Enum):
    ROOM = auto()
    DOOR = auto()
    MINI_MAP = auto()
    PLAYER = auto()
    GUN = auto()
    BULLET = auto()