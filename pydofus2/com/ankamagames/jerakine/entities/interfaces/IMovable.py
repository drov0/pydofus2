from types import FunctionType
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
    from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath


class IMovable(IEntity):
    @property
    def isMoving(self) -> bool:
        raise NotImplementedError()

    def move(
        self,
        movePath: "MovementPath",
        callback: FunctionType = None,
        cellId=None,
    ) -> None:
        raise NotImplementedError()

    def jump(self, cellId: "MapPoint") -> None:
        pass

    def stop(self, param1: bool = False) -> None:
        raise NotImplementedError()
