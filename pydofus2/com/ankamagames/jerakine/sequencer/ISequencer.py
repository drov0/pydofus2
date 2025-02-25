from pydofus2.com.ankamagames.berilia.managers.EventsHandler import EventsHandler
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencable import ISequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencableListener import ISequencableListener


class ISequencer(ISequencableListener, EventsHandler):
    def addStep(self, param1: ISequencable) -> None:
        pass

    def start(self) -> None:
        pass

    def __str__(self) -> str:
        pass

    @property
    def defaultStepTimeout(self) -> int:
        pass

    @defaultStepTimeout.setter
    def defaultStepTimeout(self, param1: int) -> None:
        pass

    @property
    def length(self) -> int:
        pass

    @property
    def steps(self) -> list:
        pass

    def clear(self) -> None:
        pass

    @property
    def running(self) -> bool:
        pass
