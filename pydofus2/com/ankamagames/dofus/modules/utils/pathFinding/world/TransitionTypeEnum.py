from enum import Enum


class TransitionTypeEnum(Enum):

    UNSPECIFIED: int = 0

    SCROLL: int = 1

    SCROLL_ACTION: int = 2

    MAP_EVENT: int = 4

    MAP_ACTION: int = 8

    MAP_OBSTACLE: int = 16

    INTERACTIVE: int = 32

    NPC_ACTION: int = 64
