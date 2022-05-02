from types import FunctionType
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath


class IMovable(IEntity):
    @property
    def isMoving(self) -> bool:
        raise NotImplementedError()

    def move(
        self,
        param1: MovementPath,
        param2: FunctionType = None,
        param3=None,
    ) -> None:
        raise NotImplementedError()

    def jump(self, param1: MapPoint) -> None:
        pass

    def stop(self, param1: bool = False) -> None:
        raise NotImplementedError()
