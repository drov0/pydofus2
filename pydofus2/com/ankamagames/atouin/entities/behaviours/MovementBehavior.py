import threading

from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameMapMovementConfirmMessage import \
    GameMapMovementConfirmMessage
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.types.positions.MovementPath import \
    MovementPath


class MovementBehavior(threading.Thread):
    
    def __init__(self, clientMovePath: MovementPath, callback):
        super().__init__(name=threading.currentThread().name)
        self.movePath = clientMovePath
        self.currStep = self.movePath.path[0]
        self.stopEvt = threading.Event()
        self.running = threading.Event()
        self.callback = callback
        
    def stop(self):
        self.stopEvt.set()

    def isRunning(self):
        return self.running.is_set()

    def run(self):
        Logger().info(f"Movement animation started")
        self.running.set()
        for pe in self.movePath.path[1:] + [self.movePath.end]:
            if Kernel().worker.terminated.is_set():
                return
            if not PlayedCharacterManager().entity.isMoving:
                return self.callback(False)
            stepDuration = self.movePath.getStepDuration(self.currStep.orientation)
            if self.stopEvt.wait(stepDuration):
                Logger().warning(f"Movement animation stopped")
                self.running.clear()
                return self.callback(False)
            self.currStep = pe
        if Kernel().worker.terminated.is_set():
            return
        Logger().info(f"Movement animation completed")
        self.callback(True)

