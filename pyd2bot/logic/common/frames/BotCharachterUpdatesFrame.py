from com.ankamagames.dofus.datacenter.breeds.Breed import Breed
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
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
        return Priority.VERY_LOW

    def boostStat(self, statId: int, points: int):
        if statId == StatIds.STRENGTH:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForStrength
        elif statId == StatIds.VITALITY:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForVitality
        elif statId == StatIds.WISDOM:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForWisdom
        elif statId == StatIds.INTELLIGENCE:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForIntelligence
        elif statId == StatIds.AGILITY:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForAgility
        elif statId == StatIds.CHANCE:
            statFloors = Breed.getBreedById(PlayedCharacterManager().infos.breed).statsPointsForChance
        base = PlayedCharacterManager().stats.getStatAdditionalValue(statId)
        additional = PlayedCharacterManager().stats.getStatBaseValue(statId)
        logger.debug(f"Stat {statId} has base {base} and additional {additional} so totoal = {base + additional}")
        capital = base + additional
        for i in range(len(statFloors)):
            if i + 1 == len(statFloors):
                nextFloor = float("inf")
            else:
                nextFloor = statFloors[i + 1][0]
            if statFloors[i][0] <= capital < nextFloor:
                currentFloorCost = statFloors[i][1]
                break
        boost = points // currentFloorCost
        if boost > 0:
            logger.debug(f"Boosting {statId} by {boost}")
            sumsg = StatsUpgradeRequestMessage()
            sumsg.init(False, statId, boost)
            ConnectionsHandler.getConnection().send(sumsg)

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
                pointsEarned = (clumsg.newLevel - previousLevel) * 5
                self.boostStat(self.statIdToUp, pointsEarned)
            return True

        elif isinstance(msg, CharacterStatsListMessage):
            unusedStatPoints = PlayedCharacterManager().stats.getStatBaseValue(StatIds.STATS_POINTS)
            if unusedStatPoints > 0:
                self.boostStat(self.statIdToUp, unusedStatPoints)
            return True
