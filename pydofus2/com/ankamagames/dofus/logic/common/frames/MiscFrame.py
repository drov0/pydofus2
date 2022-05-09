from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from com.ankamagames.dofus.network.messages.game.approach.ServerSessionConstantsMessage import (
    ServerSessionConstantsMessage,
)
from com.ankamagames.dofus.network.messages.game.approach.ServerSettingsMessage import ServerSettingsMessage
from com.ankamagames.dofus.network.messages.game.basic.CurrentServerStatusUpdateMessage import (
    CurrentServerStatusUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.houses.AccountHouseMessage import AccountHouseMessage
from com.ankamagames.dofus.network.messages.security.CheckFileMessage import CheckFileMessage
from com.ankamagames.dofus.network.messages.security.CheckFileRequestMessage import CheckFileRequestMessage
from com.ankamagames.dofus.network.messages.web.haapi.HaapiApiKeyMessage import HaapiApiKeyMessage
from com.ankamagames.dofus.network.messages.web.haapi.HaapiAuthErrorMessage import HaapiAuthErrorMessage
from com.ankamagames.dofus.network.messages.web.haapi.HaapiSessionMessage import HaapiSessionMessage
from com.ankamagames.dofus.network.types.game.approach.ServerSessionConstant import ServerSessionConstant
from com.ankamagames.dofus.network.types.game.approach.ServerSessionConstantInteger import ServerSessionConstantInteger
from com.ankamagames.dofus.network.types.game.approach.ServerSessionConstantLong import ServerSessionConstantLong
from com.ankamagames.dofus.network.types.game.approach.ServerSessionConstantString import ServerSessionConstantString
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.enums.Priority import Priority

logger = Logger("Dofus2")


class MiscFrame(Frame, metaclass=Singleton):

    SERVER_CONST_TIME_BEFORE_DISCONNECTION: int = 1

    SERVER_CONST_KOH_DURATION: int = 2

    SERVER_CONST_KOH_WINNING_SCORE: int = 3

    SERVER_CONST_MINIMAL_TIME_BEFORE_KOH: int = 4

    SERVER_CONST_TIME_BEFORE_WEIGH_IN_KOH: int = 5

    _serverSessionConstants: dict

    _mouseOnStage: bool = True

    _serverStatus: int

    def __init__(self):
        super().__init__()

    def pushed(self) -> bool:
        self._serverSessionConstants = dict()
        return True

    def pulled(self) -> bool:
        return True

    def getServerSessionConstant(self, id: int) -> object:
        return self._serverSessionConstants[id]

    def getServerStatus(self) -> int:
        return self._serverStatus

    def process(self, msg: Message) -> bool:

        if isinstance(msg, ServerSettingsMessage):
            ssmsg = msg
            PlayerManager().serverCommunityId = ssmsg.community
            PlayerManager().serverLang = ssmsg.lang
            PlayerManager().serverGameType = ssmsg.gameType
            PlayerManager().serverIsMonoAccount = ssmsg.isMonoAccount
            PlayerManager().arenaLeaveBanTime = ssmsg.arenaLeaveBanTime
            PlayerManager().hasFreeAutopilot = ssmsg.hasFreeAutopilot
            return True

        if isinstance(msg, ServerSessionConstantsMessage):
            sscmsg = msg
            self._serverSessionConstants = dict()
            for constant in sscmsg.variables:
                if isinstance(constant, ServerSessionConstantInteger):
                    self._serverSessionConstants[constant.id] = constant.value
                elif isinstance(constant, ServerSessionConstantLong):
                    self._serverSessionConstants[constant.id] = constant.value
                elif isinstance(constant, ServerSessionConstantString):
                    self._serverSessionConstants[constant.id] = constant.value
                else:
                    self._serverSessionConstants[constant.id] = None
            return True

        if isinstance(msg, CurrentServerStatusUpdateMessage):
            cssum = msg
            self._serverStatus = cssum.status
            return True

        if isinstance(msg, AccountHouseMessage):
            ahm = msg
            # if not Kernel().getWorker().getFrame('HouseFrame'):
            #     Kernel.getWorker().addFrame(HouseFrame())
            # houseFrame = Kernel().getWorker().getFrame('HouseFrame')
            # if houseFrame is not None:
            #     houseFrame.process(msg)
            return True

        if isinstance(msg, HaapiSessionMessage):
            hsm = msg
            # if hsm.type == HaapiSessionTypeEnum.HAAPI_ACCOUNT_SESSION:
            #     HaapiKeyManager().saveAccountSessionId(hsm.key)
            # else:
            #     if hsm.type != HaapiSessionTypeEnum.HAAPI_GAME_SESSION:
            #         return False
            #     HaapiKeyManager().saveGameSessionId(hsm.key)
            return True

        if isinstance(msg, HaapiApiKeyMessage):
            hakmsg = msg
            # logStr = "RECEIVED API KEY : "
            # if hakmsg != null and hakmsg.token != null and len(hakmsg.token) >= 5:
            #     logStr += hakmsg.token.substr(0, 5)
            # logger.debug(logStr)
            # HaapiKeyManager().saveApiKey(hakmsg.token)
            return True

        if isinstance(msg, HaapiAuthErrorMessage):
            haem = msg
            # logger.debug("ERROR ON ASKING API KEY type=" + haem.type + ", id=" + haem.getMessageId())
            # if haem.type == HaapiAuthTypeEnum.HAAPI_API_KEY:
            #     logger.error("Error during ApiKey request.")
            return True
        else:
            return False

    @property
    def priority(self) -> int:
        return Priority.LOW