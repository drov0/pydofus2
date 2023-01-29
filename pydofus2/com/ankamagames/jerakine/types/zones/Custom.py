from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.types.zones.IZone import IZone


class Custom(IZone):

    _aCells: list[int]

    def __init__(self, cells: list[int]):
        super().__init__()
        self._aCells = cells

    @property
    def radius(self) -> int:
        raise NotImplementedError()

    @radius.setter
    def radius(self, n: int) -> None:
        raise NotImplementedError()

    @property
    def minRadius(self) -> int:
        raise NotImplementedError()

    @minRadius.setter
    def minRadius(self, r: int) -> None:
        raise NotImplementedError()

    @property
    def surface(self) -> int:
        return len(self._aCells)

    @property
    def direction(self) -> int:
        raise NotImplementedError()

    @direction.setter
    def direction(self, d: int) -> None:
        raise NotImplementedError()

    def getCells(self, cellId: int = 0) -> list[int]:
        return self._aCells
