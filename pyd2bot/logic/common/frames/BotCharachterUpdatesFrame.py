from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.network.messages.game.achievement.AchievementFinishedMessage import (
    AchievementFinishedMessage,
)
from com.ankamagames.dofus.network.messages.game.achievement.AchievementRewardRequestMessage import (
    AchievementRewardRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.character.stats.CharacterLevelUpMessage import CharacterLevelUpMessage
from com.ankamagames.dofus.network.messages.game.character.stats.CharacterStatsListMessage import (
    CharacterStatsListMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.stats.StatsUpgradeRequestMessage import (
    StatsUpgradeRequestMessage,
)
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicDetailed import (
    CharacterCharacteristicDetailed,
)
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from damageCalculation.tools import StatIds

logger = Logger("Dofus2")


class BotCharachterUpdatesFrame(Frame):
    statIdToUp = None

    def __init__(self):
        if self.statIdToUp is None:
            logger.warning("You didn't define any stat to up")
        self._myTurn = False
        super().__init__()

    def pushed(self) -> bool:
        return True

    def pulled(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return Priority.ULTIMATE_HIGHEST_DEPTH_OF_DOOM

    def process(self, msg: Message) -> bool:

        if isinstance(msg, AchievementFinishedMessage):
            msg.achievement.id
            arrmsg = AchievementRewardRequestMessage()
            arrmsg.init(msg.achievement.id)
            ConnectionsHandler.getConnection().send(arrmsg)
            return False

        elif isinstance(msg, CharacterLevelUpMessage):
            clumsg = msg
            if self.statIdToUp:
                previousLevel = PlayedCharacterManager().infos.level
                PlayedCharacterManager().infos.level = clumsg.newLevel
                caracPointEarned = (clumsg.newLevel - previousLevel) * 5
                sumsg = StatsUpgradeRequestMessage()
                sumsg.init(False, self.statIdToUp, caracPointEarned)
                ConnectionsHandler.getConnection().send(sumsg)
                return False

        elif isinstance(msg, CharacterStatsListMessage):
            for char in msg.stats.characteristics:
                if isinstance(char, CharacterCharacteristicDetailed) and char.characteristicId == StatIds.STATS_POINTS:
                    if char.base > 0:
                        sumsg = StatsUpgradeRequestMessage()
                        sumsg.init(False, self.statIdToUp, char.base)
                        ConnectionsHandler.getConnection().send(sumsg)
                        return False
