import asyncio
import locale
import threading
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from time import perf_counter, sleep
from typing import TYPE_CHECKING

from pyd2bot.thriftServer.pyd2botService.ttypes import DofusError
from pydofus2.com.ankamagames.atouin.Haapi import Haapi
from pydofus2.com.ankamagames.atouin.resources.adapters.ElementsAdapter import ElementsAdapter
from pydofus2.com.ankamagames.berilia.managers.EventsHandler import Listener
from pydofus2.com.ankamagames.berilia.managers.KernelEvent import KernelEvent
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
    KernelEventsManager
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import \
    DisconnectionReason
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.frames.QueueFrame import \
    QueueFrame
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import \
    PlayerManager
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import \
    LoginValidationWithTokenAction
from pydofus2.com.ankamagames.dofus.logic.connection.frames.AuthentificationFrame import \
    AuthentificationFrame
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import \
    AuthentificationManager
from pydofus2.com.ankamagames.dofus.logic.game.approach.frames.GameServerApproachFrame import \
    GameServerApproachFrame
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.jerakine.data.ModuleReader import ModuleReader
from pydofus2.com.ankamagames.jerakine.data.XmlConfig import XmlConfig
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.messages.TerminateWorkerMessage import \
    TerminateWorkerMessage
from pydofus2.com.ankamagames.jerakine.resources.adapters.AdapterFactory import AdapterFactory

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import \
        ServerConnection

# Set the locale to the locale identifier associated with the current language
# The '.UTF-8' suffix specifies the character encoding
locale.setlocale(locale.LC_ALL, Kernel().getLocaleLang() + '.UTF-8')

class DofusClient(threading.Thread):
    APIKEY_NOT_FOUND = 36363
    UNEXPECTED_CLIENT_ERROR = 36364
    lastLoginTime = None
    minLoginInterval = 60 * 3
    LOGIN_TIMEOUT = 35
    MAX_CONN_TRIES = 3

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
        self._conxTries = 0
        self._connectionUnexpectedFailureTimes = []
        self.mule = False
        self.mitm = False
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
        AdapterFactory.addAdapter("ele", ElementsAdapter)
        AdapterFactory.addAdapter("dlm", MapsAdapter)
        Kernel().isMule = self.mule
        Kernel().mitm = self.mitm
        ModuleReader._clearObjectsCache = True
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

    def onCrash(self, event, message, reason=DisconnectionReasonEnum.EXCEPTION_THROWN):
        Logger().error(f"Client crashed for reason : {message}")
        self._crashed = True
        self._crashMessage = message
        self._shutDownReason = f"Crashed for reason: {message}"
        self.onShutdown(event, message, reason)

    def onShutdown(self, event, message, reason=None):
        Logger().debug(f"[DofusClient] Shutdown requested for reason: {message}")
        self.shutdown(reason, message)

    def onRestart(self, event, message):
        self.onReconnect(event, message)

    def onLoginTimeout(self, listener: Listener):
        self.worker.process(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))
        listener.armTimer()
        self.lastLoginTime = perf_counter()

    def initListeners(self):
        KernelEventsManager().once(
            KernelEvent.CharacterSelectedSuccessfully,
            self.onCharacterSelectionSuccess,
            originator=self,
        )
        KernelEventsManager().once(
            KernelEvent.MapDataProcessed,
            self.onInGame,
            timeout=self.LOGIN_TIMEOUT,
            ontimeout=self.onLoginTimeout,
            originator=self,
        )
        KernelEventsManager().on(KernelEvent.ClientCrashed, self.onCrash, originator=self)
        KernelEventsManager().on(KernelEvent.ClientShutdown, self.onShutdown, originator=self)
        KernelEventsManager().on(KernelEvent.ClientRestart, self.onRestart, originator=self)
        KernelEventsManager().on(KernelEvent.ClientReconnect, self.onReconnect, originator=self)
        KernelEventsManager().on(KernelEvent.ClientClosed, self.onConnectionClosed, originator=self)
        KernelEventsManager().on(KernelEvent.FightStarted, self.onFight)

    def onConnectionClosed(self, event, connId):
        reason = ConnectionsHandler().handleDisconnection()
        Logger().info(f"Connection '{connId}' closed for reason : {reason}")
        if ConnectionsHandler().hasReceivedMsg:
            if (
                not reason.expected
                and not ConnectionsHandler().hasReceivedNetworkMsg
                and self._conxTries < self.MAX_CONN_TRIES
            ):
                Logger().error(
                    f"The connection was closed unexpectedly. Reconnection attempt {self._conxTries}/{self.MAX_CONN_TRIES}."
                )
                if not Kernel().mitm:      
                    self._conxTries += 1
                    self._connectionUnexpectedFailureTimes.append(perf_counter())
                    self.onReconnect(None, reason.message)
            else:
                if not reason.expected:
                    self._connectionUnexpectedFailureTimes.append(perf_counter())
                    self.onReconnect(None, "The connection was closed unexpectedly.")
                else:
                    if reason.type == DisconnectionReasonEnum.EXCEPTION_THROWN:
                        self.onCrash(None, reason.message, reason.type)
                    elif reason.type == DisconnectionReasonEnum.WANTED_SHUTDOWN:
                        self.shutdown(reason.type, reason.message)
                    elif reason.type in [DisconnectionReasonEnum.RESTARTING, DisconnectionReasonEnum.DISCONNECTED_BY_POPUP, DisconnectionReasonEnum.CONNECTION_LOST]:
                        self.onRestart(None, reason.message)
                    elif reason.type == DisconnectionReasonEnum.SWITCHING_TO_GAME_SERVER:
                        Kernel().worker.addFrame(GameServerApproachFrame())
                        ConnectionsHandler().connectToGameServer(
                            Kernel().serverSelectionFrame._selectedServer.address,
                            Kernel().serverSelectionFrame._selectedServer.ports[0],
                        )
                    elif reason.type == DisconnectionReasonEnum.CHANGING_SERVER:
                        if not AuthentificationManager()._lva or AuthentificationManager()._lva.serverId is None:
                            Logger().error(
                                f"Closed connection to change server but no serverId is specified in Auth Manager"
                            )
                        else:
                            Logger().info(
                                f"Switching to {AuthentificationManager()._lva.serverId} server ..."
                            )
                            Kernel().worker.addFrame(AuthentificationFrame())
                            Kernel().worker.addFrame(QueueFrame())
                            Kernel().worker.process(
                                LoginValidationWithTokenAction.create(
                                    AuthentificationManager()._lva.serverId != 0,
                                    AuthentificationManager()._lva.serverId,
                                )
                            )
                    elif reason.type == DisconnectionReasonEnum.SWITCHING_TO_HUMAN_VENDOR:
                        pass
                    
                    elif reason.type == DisconnectionReasonEnum.DISCONNECTED_BY_USER:
                        pass
        else:
            Logger().warning("The connection hasn't even start or already closed.")

    def onFight(self):
        Logger().debug("Fight started")
        
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

    def onReconnect(self, event, message, afterTime=0):
        Logger().warning(f"Reconnect requested for reason: {message}")
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self._reconnectRecord.append({"restartTime": formatted_time, "reason": message})
        Kernel().reset(reloadData=True)
        if afterTime:
            sleep(afterTime)
        self.initListeners()
        self.prepareLogin()
        self.worker.process(LoginValidationWithTokenAction.create(self._serverId != 0, self._serverId))

    def waitNextLogin(self):
        if DofusClient.lastLoginTime is not None:
            diff = DofusClient.minLoginInterval - (perf_counter() - DofusClient.lastLoginTime)
            if diff > 0:
                Logger().info(f"ave to wait {diff}sec before reconnecting again")
                self.terminated.wait(diff)
        self.lastLoginTime = perf_counter()

    def shutdown(self, reason=DisconnectionReasonEnum.WANTED_SHUTDOWN, msg=""):
        self._shutDownReason = reason
        if Kernel.getInstance(self.name):
            Kernel.getInstance(self.name).worker.process(TerminateWorkerMessage())
        return

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
            self.onShutdown(None, f"Wanted shutdown for reason : {self._shutDownReason}", DisconnectionReasonEnum.EXCEPTION_THROWN)
        Kernel().reset()
        Logger().info("goodby crual world")
        self.terminated.set()
