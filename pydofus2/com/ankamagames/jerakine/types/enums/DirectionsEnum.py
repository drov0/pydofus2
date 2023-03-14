from enum import Enum


class DirectionsEnum(Enum):
    RIGHT = 0
    DOWN_RIGHT = 1
    DOWN = 2
    DOWN_LEFT = 3
    LEFT = 4
    UP_LEFT = 5
    UP = 6
    UP_RIGHT = 7
    UDEFINED = -1

    @classmethod
    def getMapChangeDirections(cls):
        return [cls.RIGHT, cls.DOWN, cls.LEFT, cls.UP]
