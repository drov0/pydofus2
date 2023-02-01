import threading
from types import FunctionType
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
import threading

lock = threading.Lock()


class BenchmarkTimer(threading.Thread):
    _createdTimers = dict[str, list["BenchmarkTimer"]]()
    _timers_count = 0
    _started_timers_count = 0

    def __init__(self, interval: int, function: FunctionType, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.callerName = function.__name__
        self.parent = threading.current_thread()
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()
        BenchmarkTimer._timers_count += 1
        with lock:
            if self.parent.name not in BenchmarkTimer._createdTimers:
                BenchmarkTimer._createdTimers[self.parent.name] = []
            BenchmarkTimer._createdTimers[self.parent.name].append(self)
        self.name = self.parent.name

    def printUnstoppedTimers(self) -> None:
        for timer in BenchmarkTimer._createdTimers:
            Logger().info(f"{timer.name} is still running")
        Logger().info(f"Total unstopped Timers: {len(BenchmarkTimer._createdTimers)}")

    def start(self) -> None:
        BenchmarkTimer._started_timers_count += 1
        super().start()
        # sumAllTimers = sum([len(timers) for timers in BenchmarkTimer._createdTimers.values()])
        # Logger().info(f"{self.callerName} in timer  Total Timers in all threads: {sumAllTimers}")

    def cancel(self) -> None:
        self.finished.set()

    @classmethod
    def clear(cls) -> None:
        thname = threading.current_thread().name
        while cls._createdTimers[thname]:
            timer = cls._createdTimers[thname].pop()
            if timer:
                timer.cancel()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        if self in BenchmarkTimer._createdTimers[self.parent.name]:
            BenchmarkTimer._createdTimers[self.parent.name].remove(self)
        BenchmarkTimer._started_timers_count -= 1
        BenchmarkTimer._timers_count -= 1
