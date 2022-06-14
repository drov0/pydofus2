from enum import Enum


class Priority(Enum):
    LOG: int = 10

    ULTIMATE_HIGHEST_DEPTH_OF_DOOM: int = 3

    HIGHEST: int = 2

    HIGH: int = 1

    NORMAL: int = 0

    LOW: int = -1

    VERY_LOW = -2

    LOWEST: int = -3
