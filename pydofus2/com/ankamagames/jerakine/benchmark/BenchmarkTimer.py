from threading import Timer
from types import FunctionType
from pydofus2.com.ankamagames.jerakine.benchmark.FileLoggerEnum import FileLoggerEnum
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger("Dofus2")


class BenchmarkTimer(Timer):

    startedTimers = set["BenchmarkTimer"]()
    name: str = "unamed"

    def __init__(self, interval: int, function: FunctionType, *args, **kwargs):
        self.interval = interval
        self.name = function.__name__
        super().__init__(interval, function, *args, **kwargs)
        BenchmarkTimer.startedTimers.add(self)

    def printUnstoppedTimers(self) -> None:
        for timer in BenchmarkTimer.startedTimers:
            logger.info(f"{timer.name} is still running")
        logger.info(f"Total unstopped Timers: {len(BenchmarkTimer.startedTimers)}")

    def start(self) -> None:
        super().start()
        if self not in BenchmarkTimer.startedTimers:
            BenchmarkTimer.startedTimers.add(self)
        self.hasBeenReset = False

    def cancel(self) -> None:
        super().cancel()
        if self in BenchmarkTimer.startedTimers:
            BenchmarkTimer.startedTimers.remove(self)
