from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.IPausableSequencable import IPausableSequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencableListener import ISequencableListener

logger = Logger("Dofus2")


class AbstractSequencable(IPausableSequencable):

    DEFAULT_TIMEOUT: int = 2

    _stepListeners: set = None

    _timeOut: BenchmarkTimer = None

    _castingSpellId: int = -1

    _timeoutMax: int = None

    _timeoutInterval = -1

    _withTimeOut: bool = False

    _paused: bool = False

    _finished: bool = False

    def __init__(self):
        self._stepListeners = set()
        self._timeoutMax = self.DEFAULT_TIMEOUT
        super().__init__()

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def timeout(self) -> int:
        return self._timeoutMax

    @property
    def finished(self) -> bool:
        return self._finished

    @finished.setter
    def finished(self, bool: bool) -> None:
        self._finished = bool

    @timeout.setter
    def timeout(self, value: int) -> None:
        self._timeoutMax = value
        if self._timeOut and value != -1:
            self._timeoutInterval = value

    @property
    def hasDefaultTimeout(self) -> bool:
        return self._timeoutMax == self.DEFAULT_TIMEOUT

    def pause(self) -> None:
        if self._timeOut:
            self._timeOut.cancel()
        self._paused = True

    def resume(self) -> None:
        self._paused = False
        if self._timeOut:
            self._timeOut.start()

    def start(self) -> None:
        pass

    def addListener(self, listener: ISequencableListener) -> None:
        if not self._timeOut and self._timeoutMax != -1:
            self._timeOut = BenchmarkTimer(self._timeoutMax, self.onTimeOut)
            self._timeOut.start()
        if not self._stepListeners:
            self._stepListeners = set()
        self._stepListeners.add(listener)

    def executeCallbacks(self) -> None:
        # FightProfiler().stop()
        if self._timeOut:
            self._timeOut.cancel()
            self._timeOut = None
        self._finished = True
        if self._stepListeners:
            for listener in self._stepListeners.copy():
                if listener:
                    listener.stepFinished(self, self._withTimeOut)

    def removeListener(self, listener: ISequencableListener) -> None:
        if not self._stepListeners:
            return
        self._stepListeners.remove(listener)

    def __str__(self) -> str:
        return self.__class__.__name__

    def clear(self) -> None:
        if self._timeOut:
            self._timeOut.stop()
        self._timeOut = None
        self._stepListeners = None

    @property
    def castingSpellId(self) -> int:
        return self._castingSpellId

    @castingSpellId.setter
    def castingSpellId(self, val: int) -> None:
        self._castingSpellId = val

    @property
    def isTimeout(self) -> bool:
        return self._withTimeOut

    def onTimeOut(self) -> None:
        logger.error(f"Time out sur la step {self} ({self._timeOut}")
        self._withTimeOut = True
        if self._timeOut:
            self._timeOut.cancel()
        self._timeOut = None
        self.executeCallbacks()
        self._stepListeners = None
