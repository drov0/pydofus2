from types import FunctionType
from com.ankamagames.jerakine.entities.behaviours.IMovementBehavior import (
    IMovementBehavior,
)
from com.ankamagames.jerakine.entities.interfaces.IDisplayBehavior import (
    IDisplayBehavior,
)
from com.ankamagames.jerakine.entities.interfaces.IDisplayable import IDisplayable
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.entities.interfaces.IMovable import IMovable
from com.ankamagames.jerakine.interfaces.IRectangle import IRectangle
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath


class Projectile(IDisplayable, IMovable, IEntity):

    logger = Logger("pyd2bot")

    _id: float

    _position: MapPoint

    _displayed: bool

    _displayBehavior: IDisplayBehavior

    _movementBehavior: IMovementBehavior

    _transparencyAllowed: bool = True

    startPlayingOnlyWhenDisplayed: bool

    def __init__(
        self,
        nId: float,
        look,
        postInit: bool = False,
        startPlayingOnlyWhenDisplayed: bool = True,
    ):
        super().__init__(look)
        self.startPlayingOnlyWhenDisplayed = startPlayingOnlyWhenDisplayed
        self.id = nId
        if not postInit:
            self.initDirection()

    @property
    def displayBehaviors(self) -> IDisplayBehavior:
        return self._displayBehavior

    @displayBehaviors.setter
    def displayBehaviors(self, oValue: IDisplayBehavior) -> None:
        self._displayBehavior = oValue

    @property
    def movementBehavior(self) -> IMovementBehavior:
        return self._movementBehavior

    @movementBehavior.setter
    def movementBehavior(self, oValue: IMovementBehavior) -> None:
        self._movementBehavior = oValue

    @property
    def id(self) -> float:
        return self._id

    @id.setter
    def id(self, nValue: float) -> None:
        self._id = nValue

    @property
    def position(self) -> MapPoint:
        return self._position

    @position.setter
    def position(self, oValue: MapPoint) -> None:
        self._position = oValue

    @property
    def isMoving(self) -> bool:
        return self._movementBehavior.isMoving(self)

    @property
    def absoluteBounds(self) -> IRectangle:
        return self._displayBehavior.getAbsoluteBounds(self)

    @property
    def displayed(self) -> bool:
        return self._displayed

    def initDirection(self, direction: int = -1) -> None:
        pass

    def display(self, strata: int = 0) -> None:
        self._displayBehavior.display(self, strata)
        self._displayed = True

    def remove(self) -> None:
        self._displayed = False
        self._displayBehavior.remove(self)
        self.clearAnimation()

    def destroy(self) -> None:
        self.remove()
        super().destroy()

    def move(
        self,
        path: MovementPath,
        callback: FunctionType = None,
        movementBehavior: IMovementBehavior = None,
    ) -> None:
        self._movementBehavior.move(self, path, callback)

    def jump(self, newPosition: MapPoint) -> None:
        self._movementBehavior.jump(self, newPosition)

    def stop(self, forceStop: bool = False) -> None:
        self._movementBehavior.stop(self)
