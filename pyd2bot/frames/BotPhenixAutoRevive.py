from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import RoleplayInteractivesFrame
from com.ankamagames.dofus.network.enums.PlayerLifeStatusEnum import PlayerLifeStatusEnum
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayFreeSoulRequestMessage import (
    GameRolePlayFreeSoulRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayPlayerLifeStatusMessage import (
    GameRolePlayPlayerLifeStatusMessage,
)
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.messages.AutoTripEndedMessage import AutoTripEndedMessage

logger = Logger("Dofus2")


class BotPhenixAutoRevive(Frame):
    PHENIX_MAPID = None

    def __init__(self, phenixMapId):
        super().__init__()

    def pushed(self) -> bool:
        self._waitingForMapData = False
        if PlayerLifeStatusEnum(PlayedCharacterManager().state) == PlayerLifeStatusEnum.STATUS_PHANTOM:
            Kernel().getWorker().addFrame(BotAutoTripFrame(self.PHENIX_MAPID))
        elif PlayedCharacterManager().state == PlayerLifeStatusEnum.STATUS_TOMBSTONE:
            self.releaseSoul()
        return True

    def pulled(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return Priority.HIGH

    def process(self, msg: Message) -> bool:

        if isinstance(msg, AutoTripEndedMessage):
            self.clickOnPhenix()
            return True

        elif isinstance(msg, GameRolePlayPlayerLifeStatusMessage):
            if PlayedCharacterManager().state == PlayerLifeStatusEnum.STATUS_PHANTOM:
                self._waitingForMapData = True
            else:
                logger.info("Player is not in phantom state will renmove the phenix frame")
                Kernel().getWorker().removeFrame(self)
            return False

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._waitingForMapData:
                Kernel().getWorker().addFrame(BotAutoTripFrame(self.PHENIX_MAPID))
                self._waitingForMapData = False
            return False

    def clickOnPhenix(self):
        interactives: "RoleplayInteractivesFrame" = Kernel().getWorker().getFrame("RoleplayInteractivesFrame")
        if interactives:
            reviveSkill = interactives.getReviveIe()
            interactives.skillClicked(reviveSkill)

    def releaseSoul(self):
        grpfsrmmsg = GameRolePlayFreeSoulRequestMessage()
        ConnectionsHandler.getConnection().send(grpfsrmmsg)
