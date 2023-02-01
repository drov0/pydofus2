import sys
from whistle import EventDispatcher
from pydofus2.com.ankamagames.jerakine.events.SequencerEvent import SequencerEvent
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.IPausableSequencable import IPausableSequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencable import ISequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from pydofus2.com.ankamagames.jerakine.sequencer.ISubSequenceSequencable import (
    ISubSequenceSequencable,
)
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class SerialSequencer(ISequencer, EventDispatcher):

    DEFAULT_SEQUENCER_NAME: str = "SerialSequencerDefault"

    SEQUENCERS: dict = dict()

    _aStep: list[ISequencable]

    _currentStep: ISequencable = None

    _lastStep: ISequencable = None

    _running: bool = False

    _type: str = None

    _activeSubSequenceCount: int

    _paused: bool = None

    _defaultStepTimeout: int = -2147483648

    def __init__(self, type: str = "SerialSequencerDefault"):
        self._aStep = list()
        self._activeSubSequenceCount = 0
        super().__init__()
        if not self.SEQUENCERS.get(type):
            self.SEQUENCERS[type] = dict()
        self.SEQUENCERS[type][self] = True

    @classmethod
    def clearByType(cls, type: str) -> None:
        seq = None
        for seq in cls.SEQUENCERS[type]:
            SerialSequencer(seq).clear()
        del cls.SEQUENCERS[type]

    @property
    def currentStep(self) -> ISequencable:
        return self._currentStep

    @property
    def lastStep(self) -> ISequencable:
        return self._lastStep

    @property
    def length(self) -> int:
        return len(self._aStep)

    @property
    def running(self) -> bool:
        return self._running

    @property
    def steps(self) -> list:
        return self._aStep

    @property
    def defaultStepTimeout(self) -> int:
        return self._defaultStepTimeout

    @defaultStepTimeout.setter
    def defaultStepTimeout(self, v: int) -> None:
        self._defaultStepTimeout = v

    def pause(self) -> None:
        self._paused = True
        if isinstance(self._currentStep, IPausableSequencable):
            self._currentStep.pause()

    def resume(self) -> None:
        self._paused = False
        if isinstance(self._currentStep, IPausableSequencable):
            self._currentStep.start()

    def add(self, item: ISequencable) -> None:
        if item:
            self.addStep(item)
        else:
            Logger().error("Tried to add a null step to the LUA script sequence, self step will be ignored")

    def addStep(self, item: ISequencable) -> None:
        self._aStep.append(item)

    def start(self) -> None:
        if not self._running:
            self._running = len(self._aStep) != 0
            if self._running:
                while len(self._aStep) > 0 and self._running:
                    self.execute()
                    if (
                        self._currentStep
                        and isinstance(self._currentStep, AbstractSequencable)
                        and not self._currentStep.finished
                    ):
                        self._running = False
            else:
                Logger().debug("[Sequencer] start asked but already running")
                self.dispatch(SequencerEvent.SEQUENCE_END, SequencerEvent(self))

    def clear(self) -> None:
        step: ISequencable = None
        self._lastStep = None
        if self._currentStep:
            self._currentStep.clear()
            self._currentStep = None
        for step in self._aStep:
            if step:
                step.clear()
        self._aStep = list()
        self._running = False

    def __str__(self) -> str:
        res: str = ""
        for step in self._aStep:
            res += str(step) + "\n"
        return res

    def execute(self) -> None:
        self._lastStep = self._currentStep
        self._currentStep = self._aStep.pop(0)
        if not self._currentStep:
            return
        self._currentStep.addListener(self)
        try:
            if isinstance(self._currentStep, ISubSequenceSequencable):
                self._activeSubSequenceCount += 1
                self._currentStep.add_listener(SequencerEvent.SEQUENCE_END, self.onSubSequenceEnd)
            if self._defaultStepTimeout != -sys.maxsize + 1 and self._currentStep.hasDefaultTimeout:
                self._currentStep.timeout = self._defaultStepTimeout
            if self.has_listeners(SequencerEvent.SEQUENCE_STEP_START):
                self.dispatch(
                    SequencerEvent.SEQUENCE_STEP_START,
                    SequencerEvent(self, self._currentStep),
                )
            self._currentStep.start()
        except Exception as e:
            if isinstance(self._currentStep, ISubSequenceSequencable):
                self._activeSubSequenceCount -= 1
                self._currentStep.remove_listener(SequencerEvent.SEQUENCE_END, self.onSubSequenceEnd)
            Logger().error(f"Exception on step {self._currentStep}", exc_info=True)
            if isinstance(self._currentStep, AbstractSequencable):
                self._currentStep.finished = True
            self.stepFinished(self._currentStep)

    def stepFinished(self, step: ISequencable, withTimout: bool = False) -> None:
        step.removeListener(self)
        if self._running:
            if self.has_listeners(SequencerEvent.SEQUENCE_STEP_FINISH):
                self.dispatch(
                    SequencerEvent.SEQUENCE_STEP_FINISH,
                    SequencerEvent(self, self._currentStep),
                )
            self._running = len(self._aStep) != 0
            if not self._running:
                if not self._activeSubSequenceCount:
                    self.dispatch(SequencerEvent.SEQUENCE_END, SequencerEvent(self))
                else:
                    self._running = True
        else:
            if self.has_listeners(SequencerEvent.SEQUENCE_STEP_FINISH):
                self.dispatch(SequencerEvent.SEQUENCE_STEP_FINISH, SequencerEvent(self, self._currentStep))
            self.start()

    def onSubSequenceEnd(self, e: SequencerEvent) -> None:
        self._activeSubSequenceCount -= 1
        if not self._activeSubSequenceCount and len(self._aStep) <= 0:
            self._running = False
            self.dispatch(SequencerEvent.SEQUENCE_END, SequencerEvent(self))
