import sys
from whistle import EventDispatcher
from com.ankamagames.jerakine.events.SequencerEvent import SequencerEvent
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.messages.Worker import Worker
from com.ankamagames.jerakine.sequencer.IPausableSequencable import IPausableSequencable
from com.ankamagames.jerakine.sequencer.ISequencable import ISequencable
from com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from com.ankamagames.jerakine.sequencer.ISubSequenceSequencable import (
    ISubSequenceSequencable,
)
from com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable

logger = Logger("Dofus2")


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
            logger.error("Tried to add a null step to the LUA script sequence, self step will be ignored")

    def addStep(self, item: ISequencable) -> None:
        self._aStep.append(item)

    def start(self) -> None:
        if self._running:
            logger.debug("[Sequencer] start asked but already running")
        if not self._running:
            self._running = len(self._aStep) != 0
            if self._running:
                while len(self._aStep) > 0 and self._running:
                    # logger.debug(f"[Sequencer] running on current step {self._currentStep}")
                    self.execute()
                    if (
                        self._currentStep
                        and isinstance(self._currentStep, AbstractSequencable)
                        and not self._currentStep.finished
                    ):
                        self._running = False
                    if self._running and not EnterFrameDispatcher().remainsTime():
                        self._running = False
                        worker = EnterFrameDispatcher().worker
                        worker.addSingleTreatmentAtPos(
                            self,
                            self.start,
                            [],
                            len(worker.findTreatments(None, self.start, [])),
                        )
            else:
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
        # logger.debug(f"[Sequencer] working on step {self._currentStep.__class__.__name__}")
        if not self._currentStep:
            return
        # FightProfiler().start()
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
            # logger.debug(f"Sequencer starting step {self._currentStep.__class__.__name__}")
            self._currentStep.start()
        except Exception as e:
            if isinstance(self._currentStep, ISubSequenceSequencable):
                self._activeSubSequenceCount -= 1
                self._currentStep.remove_listener(SequencerEvent.SEQUENCE_END, self.onSubSequenceEnd)
            logger.error(f"Exception on step {self._currentStep}", exc_info=True)
            if isinstance(self._currentStep, AbstractSequencable):
                self._currentStep.finished = True
            self.stepFinished(self._currentStep)

    def stepFinished(self, step: ISequencable, withTimout: bool = False) -> None:
        worker: Worker = None
        step.removeListener(self)
        if self._running:
            if withTimout:
                self.dispatch(SequencerEvent.SEQUENCE_TIMEOUT, SequencerEvent(self))
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
            worker = EnterFrameDispatcher().worker
            worker.addSingleTreatmentAtPos(self, self.start, [], len(worker.findTreatments(None, self.start, [])))

    def onSubSequenceEnd(self, e: SequencerEvent) -> None:
        self._activeSubSequenceCount -= 1
        if not self._activeSubSequenceCount and len(self._aStep) <= 0:
            self._running = False
            self.dispatch(SequencerEvent.SEQUENCE_END, SequencerEvent(self))
