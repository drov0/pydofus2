import threading
from time import perf_counter
from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.atouin.Haapi import Haapi
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import \
    DisconnectionReason
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import \
    PlayerManager
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import \
    LoginValidationWithTokenAction as LoginAction
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import \
    AuthentificationManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.messages.TerminateWorkerMessage import TerminateWorkerMessage

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection

class DofusClient(threading.Thread):

    def __init__(self, name="unknown"):
        super().__init__(name=name)
        self._killSig = threading.Event()
        self._registredInitFrames = []
        self._registredGameStartFrames = []
        self._stopReason: DisconnectionReason = None
        self._lastLoginTime = None
        self._minLoginInterval = 10
        self._lock = None
        self._certId = None
        self._apiKey = None
        self._certHash = None
        self._serverId = None
        self._characterId = None
        self._loginToken = None
        self._mule = False
        self._shutDownReason = None
        self.terminated = threading.Event()

    @property
    def worker(self):
        return Kernel().worker

    def init(self):
        Logger().info("[DofusClient] initializing")
        Kernel().init()
        Kernel().isMule = self._mule
        KernelEventsManager().once(KernelEvent.CHARACTER_SELECTION_SUCCESS, self.onCharacterSelectionSuccess)
        KernelEventsManager().once(KernelEvent.CRASH, self.onCrash)
        KernelEventsManager().once(KernelEvent.SHUTDOWN, self.onShutdown)
        KernelEventsManager().once(KernelEvent.RESTART, self.onRestart)
        KernelEventsManager().once(KernelEvent.RECONNECT, self.onReconnect)
        if self._characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = self._characterId
            PlayerManager().autoConnectOfASpecificCharacterId = self._characterId
        Logger().info("Adding game init frames")
        for frame in self._registredInitFrames:
            self.worker.addFrame(frame())
        Logger().info("[DofusClient] initialized")
        
    def registerInitFrame(self, frame):
        self._registredInitFrames.append(frame)

    def registerGameStartFrame(self, frame):
        self._registredGameStartFrames.append(frame)

    def onCharacterSelectionSuccess(self, event, return_value):
        Logger().info("Adding game start frames")
        for frame in self._registredGameStartFrames:
            self.worker.addFrame(frame())

    def onCrash(self, event, message):
        Logger().debug(f"[DofusClient] Crashed for reason: {message}")
        self.shutdown()

    def onShutdown(self, event, message):
        Logger().debug(f"[DofusClient] Shutdown requested for reason: {message}")
        self.shutdown()

    def onRestart(self, event, message):
        self.onReconnect(event, message)

    def onReconnect(self, event, message):
        Logger().warning(f"[DofusClient] Reconnect requested for reason: {message}")
        Kernel().reset(reloadData=True)
        KernelEventsManager().once(KernelEvent.CHARACTER_SELECTION_SUCCESS, self.onCharacterSelectionSuccess)
        KernelEventsManager().once(KernelEvent.CRASH, self.onCrash)
        KernelEventsManager().once(KernelEvent.SHUTDOWN, self.onShutdown)
        KernelEventsManager().once(KernelEvent.RESTART, self.onRestart)
        KernelEventsManager().once(KernelEvent.RECONNECT, self.onReconnect)
        if self._characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = self._characterId
            PlayerManager().autoConnectOfASpecificCharacterId = self._characterId        
        for frame in self._registredInitFrames:
            self.worker.addFrame(frame())
        token = Haapi().getLoginToken(self._certId, self._certHash, apiKey=self._apiKey)
        AuthentificationManager().setToken(token)
        self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))

    def shutdown(self, reason=DisconnectionReasonEnum.WANTED_SHUTDOWN, msg=""):
        self._shutDownReason = reason
        Kernel.getInstance(self.name).worker.process(TerminateWorkerMessage())    
        return self.terminated.wait(20)    

    @property
    def connection(self) -> "ServerConnection":
        return ConnectionsHandler().conn

    @property
    def registeredInitFrames(self) -> list:
        return self._registredInitFrames

    @property
    def registeredGameStartFrames(self) -> list:
        return self._registredGameStartFrames

    def run(self):
        try:
            self.init()
            if self._lastLoginTime is not None and perf_counter() - self._lastLoginTime < self._minLoginInterval:
                Logger().info("[DofusClient] Login request too soon, will wait some time")
                self._killSig.wait(self._minLoginInterval - (perf_counter() - self._lastLoginTime))
            self._lastLoginTime = perf_counter()
            if not self._loginToken:            
                if not self._apiKey:
                    raise Exception("No API key provided")
                self._loginToken = Haapi().getLoginToken(self._certId, self._certHash, apiKey=self._apiKey)
            AuthentificationManager().setToken(self._loginToken)
            self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))
            self.worker.run()
        except Exception as e:
            Logger().error(f"[DofusClient] Error in main: {e}", exc_info=True)
        if self._shutDownReason:
            Logger().info(f"Wanted shutdown for reason : {self._shutDownReason}")
        Kernel().reset()
        Logger().info("[DofusClient] Stopped")
        self.terminated.set()
