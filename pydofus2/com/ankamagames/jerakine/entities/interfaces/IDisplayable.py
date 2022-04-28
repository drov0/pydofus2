from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.jerakine.entities.interfaces.IDisplayBehavior import (
        IDisplayBehavior,
    )
from com.ankamagames.jerakine.interfaces.IRectangle import IRectangle


class IDisplayable:
    @property
    def displayBehaviors(self) -> "IDisplayBehavior":
        raise NotImplementedError()

    @displayBehaviors.setter
    def displayBehaviors(self, param1: "IDisplayBehavior") -> None:
        raise NotImplementedError()

    @property
    def displayed(self) -> bool:
        raise NotImplementedError()

    @property
    def absoluteBounds(self) -> IRectangle:
        raise NotImplementedError()

    def display(self, param1: int = 0) -> None:
        raise NotImplementedError()

    def remove(self) -> None:
        raise NotImplementedError()
