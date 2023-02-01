import threading
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import KernelEventsManager, KernelEvent
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import DisconnectionReason
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from time import perf_counter, sleep
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import (
    DisconnectionReasonEnum,
)
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import (
    LoginValidationWithTokenAction as LoginAction,
)
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import AuthentificationManager
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from pydofus2.com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider


class DofusClient(threading.Thread):
    def __init__(self, name="unknown"):
        super().__init__(name=name)
        self._killSig = threading.Event()
        self._registredInitFrames = []
        self._registredGameStartFrames = []
        self._stopReason: DisconnectionReason = None
        self._lastLoginTime = None
        self._minLoginInterval = 10

    @property
    def worker(self):
        return Kernel().worker

    def init(self):
        Logger().info("[DofusClient] initializing")
        Kernel().init()
        I18nFileAccessor()
        DataMapProvider()
        KernelEventsManager().once(KernelEvent.CHARACTER_SELECTION_SUCCESS, self._onCharacterSelectionSuccess)
        KernelEventsManager().once(KernelEvent.CRASH, self._onCrash)
        KernelEventsManager().once(KernelEvent.SHUTDOWN, self._onShutdown)
        KernelEventsManager().once(KernelEvent.RESTART, self._onRestart)
        KernelEventsManager().once(KernelEvent.RECONNECT, self._onReconnect)
        AuthentificationManager().setToken(self._loginToken)
        if self._characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = self._characterId
            PlayerManager().autoConnectOfASpecificCharacterId = self._characterId
        for frame in self._registredInitFrames:
            self.worker.addFrame(frame())
        Logger().info("[DofusClient] initialized")

    def setCreds(self, loginToken, serverId=0, characterId=None):
        self._serverId = serverId
        self._characterId = characterId
        self._loginToken = loginToken

    def login(self, loginToken, serverId=0, characterId=None):
        self.setCreds(loginToken, serverId, characterId)
        self.start()

    def registerInitFrame(self, frame):
        self._registredInitFrames.append(frame)

    def registerGameStartFrame(self, frame):
        self._registredGameStartFrames.append(frame)

    def _onCharacterSelectionSuccess(self, event, return_value):
        for frame in self._registredGameStartFrames:
            self.worker.addFrame(frame())

    def _onCrash(self, event, message):
        self._killSig.set()
        Logger().debug(f"[DofusClient] Crashed for reason: {message}")

    def _onShutdown(self, event, message):
        self._killSig.set()
        Logger().debug(f"[DofusClient] Shutdown requested for reason: {message}")

    def _onRestart(self, event, message):
        Logger().debug(f"[DofusClient] Restart requested for reason: {message}")

    def _onReconnect(self, event, message):
        Logger().debug(f"[DofusClient] Reconnect requested for reason: {message}")
        self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))

    def shutdown(self, reason=DisconnectionReasonEnum.WANTED_SHUTDOWN, msg=""):
        Logger().info("Shuting down ...")
        ConnectionsHandler().closeConnection(reason, msg)

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
        self.init()
        try:
            if self._lastLoginTime is not None and perf_counter() - self._lastLoginTime < self._minLoginInterval:
                Logger().info("[DofusClient] Login request too soon, will wait some time")
                sleep(self._minLoginInterval - (perf_counter() - self._lastLoginTime))
            self._lastLoginTime = perf_counter()
            self.worker.process(LoginAction.create(self._serverId != 0, self._serverId))
            while not self._killSig.is_set():
                msg = ConnectionsHandler().receive()
                self.worker.process(msg)
        except:
            Logger().error(f"[DofusClient] Error in main loop.", exc_info=True)
        Kernel().reset()
        Logger().info("[DofusClient] Stopped")
