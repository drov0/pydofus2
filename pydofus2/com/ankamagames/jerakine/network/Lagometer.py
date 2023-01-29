from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.ILagometer import ILagometer
from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage


class Lagometer(ILagometer):

    SHOW_LAG_DELAY: int = 2

    _timer: BenchmarkTimer

    _lagging: bool = False

    def __init__(self):
        super().__init__()
        self._timer = BenchmarkTimer(self.SHOW_LAG_DELAY, self.onTimerComplete)

    def ping(self, msg: INetworkMessage = None) -> None:
        self._timer = BenchmarkTimer(self.SHOW_LAG_DELAY, self.onTimerComplete)
        self._timer.start()

    def pong(self, msg: INetworkMessage = None) -> None:
        if self._lagging:
            self.stopLag()
        self.stop()

    def stop(self) -> None:
        self._timer.cancel()

    def onTimerComplete(self) -> None:
        self.stop()
        self.startLag()

    def startLag(self) -> None:
        self._lagging = True
        self.updateUi()

    def updateUi(self) -> None:
        pass

    def stopLag(self) -> None:
        self._lagging = False
        self.updateUi()
