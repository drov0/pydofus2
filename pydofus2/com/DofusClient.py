import asyncio
import threading
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from time import perf_counter
from typing import TYPE_CHECKING

from pyd2bot.thriftServer.pyd2botService.ttypes import DofusError
from pydofus2.com.ankamagames.atouin.Haapi import Haapi
from pydofus2.com.ankamagames.berilia.managers.EventsHandler import Listener
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
    LoginValidationWithTokenAction
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import \
    AuthentificationManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.messages.TerminateWorkerMessage import \
    TerminateWorkerMessage

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import \
        ServerConnection


class DofusClient(threading.Thread):
    APIKEY_NOT_FOUND = 36363
    UNEXPECTED_CLIENT_ERROR = 36364
    lastLoginTime = None
    minLoginInterval = 10
    LOGIN_TIMEOUT = 35

    def __init__(self, name="unknown"):
        super().__init__(name=name)
        self._killSig = threading.Event()
        self._registredInitFrames = []
        self._shutDownListeners = []
        self._registredGameStartFrames = []
        self._stopReason: DisconnectionReason = None
        self._lock = None
        self._certId = None
        self._apiKey = None
        self._certHash = None
        self._serverId = None
        self._characterId = None
        self._loginToken = None
        self.mule = False
        self._shutDownReason = None
        self._crashed = False
        self._crashMessage = ""
        self._reconnectRecord = []
        self.terminated = threading.Event()

    @property
    def worker(self):
        return Kernel().worker

    def init(self):
        Logger().info("[DofusClient] initializing")
        Kernel().init()
        Kernel().isMule = self.mule
        self.initListeners()
        Logger().info("[DofusClient] initialized")

    def registerInitFrame(self, frame):
        self._registredInitFrames.append(frame)

    def registerGameStartFrame(self, frame):
        self._registredGameStartFrames.append(frame)

    def onCharacterSelectionSuccess(self, event, return_value):
        Logger().info("Adding game start frames")
        for frame in self._registredGameStartFrames:
            self.worker.addFrame(frame())

    def onInGame(self, event, msg):
        Logger().info("Character entered game server successfully")

    def onCrash(self, event, message):
        Logger().debug(f"Client crashed for reason : {message}")
        self._crashed = True
        self._crashMessage = message
        self._shutDownReason = f"Crashed for reason: {message}"
        self.shutdown()

    def onShutdown(self, event, message):
        Logger().debug(f"[DofusClient] Shutdown requested for reason: {message}")
        self.shutdown()

    def onRestart(self, event, message):
        self.onReconnect(event, message)

    def onLoginTimeout(self, listener: Listener):
        self.worker.process(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))
        listener.armTimer()
        self.lastLoginTime = perf_counter()

    def initListeners(self):
        KernelEventsManager().once(
            KernelEvent.CHARACTER_SELECTION_SUCCESS,
            self.onCharacterSelectionSuccess,
            originator=self,
        )
        KernelEventsManager().once(
            KernelEvent.IN_GAME,
            self.onInGame,
            timeout=self.LOGIN_TIMEOUT,
            ontimeout=self.onLoginTimeout,
            originator=self,
        )
        KernelEventsManager().once(KernelEvent.IN_GAME, self.onInGame, originator=self)
        KernelEventsManager().once(KernelEvent.CRASH, self.onCrash, originator=self)
        KernelEventsManager().once(KernelEvent.SHUTDOWN, self.onShutdown, originator=self)
        KernelEventsManager().once(KernelEvent.RESTART, self.onRestart, originator=self)
        KernelEventsManager().once(KernelEvent.RECONNECT, self.onReconnect, originator=self)
    
    def prepareLogin(self):
        PlayedCharacterManager().instanceId = self.name
        if self._characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = int(self._characterId)
            PlayerManager().autoConnectOfASpecificCharacterId = int(self._characterId)
        Logger().info("Adding game start frames")
        for frame in self._registredInitFrames:
            self.worker.addFrame(frame())
        if not self._loginToken:
            self._loginToken = Haapi.getLoginTokenCloudScraper(self._certId, self._certHash, 1, self._apiKey)
        AuthentificationManager().setToken(self._loginToken)
        self.waitNextLogin()
        self._loginToken = None
        
    def onReconnect(self, event, message):
        Logger().warning(f"[DofusClient] Reconnect requested for reason: {message}")
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self._reconnectRecord.append({
            "restartTime": formatted_time,
            "reason": message
        })
        Kernel().reset(reloadData=True)
        self.worker.processFramesInAndOut()
        self.prepareLogin()
        if Kernel().authFrame:
            self.worker.process(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))
        else:
            Logger().warning("Authentification frame not inside worker while reconnecting!")
            self.worker.processFramesInAndOut()
            Logger().debug(self.worker._framesList)
            self.worker.processMessage(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))
    
    def waitNextLogin(self):
        if DofusClient.lastLoginTime is not None:
            diff = DofusClient.minLoginInterval - (perf_counter() - DofusClient.lastLoginTime)
            if diff > 0:
                Logger().info(f"[DofusClient] Have to wail {diff}sec before reconnecting")
                self.terminated.wait(diff)
        self.lastLoginTime = perf_counter()

    def shutdown(self, reason=DisconnectionReasonEnum.WANTED_SHUTDOWN, msg=""):
        self._shutDownReason = reason
        if Kernel.getInstance(self.name):
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
            self.prepareLogin()
            self.worker.process(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))
            self.worker.run()
        except Exception as e:
            Logger().error(f"Error in main: {e}", exc_info=True)
            self._crashMessage = str(e)
            self._crashed = True
            self._shutDownReason = f"Error in main : {str(e)}"
        if self._shutDownReason:
            Logger().info(f"Wanted shutdown for reason : {self._shutDownReason}")
        Kernel().reset()
        Logger().info("goodby crual world")
        self.terminated.set()
