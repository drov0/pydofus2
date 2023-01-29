import threading
from types import FunctionType
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
import threading

lock = threading.Lock()


class BenchmarkTimer(threading.Timer):
    _startedTimers = dict[str, set["BenchmarkTimer"]]()

    def __init__(self, interval: int, function: FunctionType, *args, **kwargs):
        super().__init__(interval, function, *args, **kwargs)
        self.interval = interval
        self.callerName = function.__name__
        self.parent = threading.current_thread()
        with lock:
            if self.parent.name not in BenchmarkTimer._startedTimers:
                BenchmarkTimer._startedTimers[self.parent.name] = set()
            BenchmarkTimer._startedTimers[self.parent.name].add(self)
        self.name = self.parent.name

    def printUnstoppedTimers(self) -> None:
        for timer in BenchmarkTimer._startedTimers:
            Logger().info(f"{timer.name} is still running")
        Logger().info(f"Total unstopped Timers: {len(BenchmarkTimer._startedTimers)}")

    def start(self) -> None:
        super().start()
        with lock:
            if self not in BenchmarkTimer._startedTimers[self.parent.name]:
                BenchmarkTimer._startedTimers[self.parent.name].add(self)

    def cancel(self) -> None:
        super().cancel()
        if self in BenchmarkTimer._startedTimers[self.parent.name]:
            BenchmarkTimer._startedTimers[self.parent.name].remove(self)
        del self

    @classmethod
    def clear(cls) -> None:
        thname = threading.current_thread().name
        while cls._startedTimers[thname]:
            timer = cls._startedTimers[thname].pop()
            if timer:
                timer.cancel()
