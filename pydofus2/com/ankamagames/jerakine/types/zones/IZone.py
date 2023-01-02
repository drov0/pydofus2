class IZone:
    @property
    def surface(self) -> int:
        raise NotImplementedError()

    @property
    def minRadius(self) -> int:
        raise NotImplementedError()

    @minRadius.setter
    def minRadius(self, param1: int) -> None:
        raise NotImplementedError()

    @property
    def direction(self) -> int:
        raise NotImplementedError()

    @direction.setter
    def direction(self, param1: int) -> None:
        raise NotImplementedError()

    @property
    def radius(self) -> int:
        raise NotImplementedError()

    @radius.setter
    def radius(self, param1: int) -> None:
        raise NotImplementedError()

    def getCells(self, param1: int = 0) -> list[int]:
        raise NotImplementedError()
