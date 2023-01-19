import threading
from types import FunctionType
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger("Dofus2")


class BenchmarkTimer(threading.Timer):
    _startedTimers = set["BenchmarkTimer"]()

    def __init__(self, interval: int, function: FunctionType, *args, **kwargs):
        super().__init__(interval, function, *args, **kwargs)
        self.interval = interval
        self.name = function.__name__
        BenchmarkTimer._startedTimers.add(self)
        self.parent = threading.current_thread()
        self.name = self.parent.name

    def printUnstoppedTimers(self) -> None:
        for timer in BenchmarkTimer._startedTimers:
            logger.info(f"{timer.name} is still running")
        logger.info(f"Total unstopped Timers: {len(BenchmarkTimer._startedTimers)}")

    def start(self) -> None:
        super().start()
        if self not in BenchmarkTimer._startedTimers:
            BenchmarkTimer._startedTimers.add(self)

    def cancel(self) -> None:
        super().cancel()
        if self in BenchmarkTimer._startedTimers:
            BenchmarkTimer._startedTimers.remove(self)
    
    @classmethod
    def clear(cls) -> None:
        while cls._startedTimers:
            timer = cls._startedTimers.pop()
            if timer:
                timer.cancel()
