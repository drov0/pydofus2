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
from pydofus2.com.ankamagames.jerakine.data.I18nFileAccessor import \
    I18nFileAccessor
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection

from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import \
    DataMapProvider


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
        self.mule = False

    @property
    def worker(self):
        return Kernel().worker

    def init(self):
        Logger().info("[DofusClient] initializing")
        Kernel().init()
        Kernel().isMule = self.mule
        I18nFileAccessor()
        DataMapProvider()
        KernelEventsManager().once(KernelEvent.CHARACTER_SELECTION_SUCCESS, self._onCharacterSelectionSuccess)
        KernelEventsManager().once(KernelEvent.CRASH, self._onCrash)
        KernelEventsManager().once(KernelEvent.SHUTDOWN, self._onShutdown)
        KernelEventsManager().once(KernelEvent.RESTART, self._onRestart)
        KernelEventsManager().once(KernelEvent.RECONNECT, self._onReconnect)
        if self._characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = self._characterId
            PlayerManager().autoConnectOfASpecificCharacterId = self._characterId
        for frame in self._registredInitFrames:
            self.worker.addFrame(frame())
        Logger().info("[DofusClient] initialized")
        
    def registerInitFrame(self, frame):
        self._registredInitFrames.append(frame)

    def registerGameStartFrame(self, frame):
        self._registredGameStartFrames.append(frame)

    def _onCharacterSelectionSuccess(self, event, return_value):
        for frame in self._registredGameStartFrames:
            self.worker.addFrame(frame())

    def _onCrash(self, event, message):
        Logger().debug(f"[DofusClient] Crashed for reason: {message}")
        self.shutdown()

    def _onShutdown(self, event, message):
        Logger().debug(f"[DofusClient] Shutdown requested for reason: {message}")
        self.shutdown()

    def _onRestart(self, event, message):
        self._onReconnect(event, message)

    def _onReconnect(self, event, message):
        Logger().debug(f"[DofusClient] Reconnect requested for reason: {message}")
        Kernel().reset(reloadData=True)
        token = Haapi().getLoginToken(self._certId, self._certHash, apiKey=self._apiKey)
        AuthentificationManager().setToken(token)
        self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))

    def shutdown(self, reason=DisconnectionReasonEnum.WANTED_SHUTDOWN, msg=""):
        Logger().info("[DofusClient] Shuting down ...")
        Kernel().reset()

    def relogin(self):
        self.login(self._loginToken, self._serverId, self._characterId)

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
            if not self._apiKey:
                raise Exception("No API key provided")
            token = Haapi().getLoginToken(self._certId, self._certHash, apiKey=self._apiKey)
            AuthentificationManager().setToken(token)
            self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))
            self.worker.run()
        except Exception as e:
            Logger().error(f"[DofusClient] Error in main: {e}", exc_info=True)
        self.shutdown()
        Logger().info("[DofusClient] Stopped")
