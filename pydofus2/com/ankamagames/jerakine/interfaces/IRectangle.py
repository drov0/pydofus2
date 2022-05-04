from com.ankamagames.jerakine.types.positions.Point import Point


class IRectangle:
    @property
    def x(self) -> float:
        raise NotImplementedError()

    @x.setter
    def x(self, param1: float) -> None:
        raise NotImplementedError()

    @property
    def y(self) -> float:
        raise NotImplementedError()

    @y.setter
    def y(self, param1: float) -> None:
        raise NotImplementedError()

    @property
    def width(self) -> float:
        raise NotImplementedError()

    @width.setter
    def width(self, param1: float) -> None:
        raise NotImplementedError()

    @property
    def height(self) -> float:
        raise NotImplementedError()

    @height.setter
    def height(self, param1: float) -> None:
        raise NotImplementedError()

    def localToGlobal(self, param1: Point) -> Point:
        raise NotImplementedError()

    def globalToLocal(self, param1: Point) -> Point:
        raise NotImplementedError()
