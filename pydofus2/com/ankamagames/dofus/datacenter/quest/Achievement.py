import re
from com.ankamagames.dofus.datacenter.items.criterion.AchievementAccountItemCriterion import (
    AchievementAccountItemCriterion,
)
from com.ankamagames.dofus.datacenter.items.criterion.GroupItemCriterion import GroupItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import IItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.LevelItemCriterion import LevelItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.PrestigeLevelItemCriterion import PrestigeLevelItemCriterion
from com.ankamagames.dofus.datacenter.quest.AchievementObjective import AchievementObjective
from com.ankamagames.dofus.datacenter.quest.Quest import Quest
from com.ankamagames.dofus.datacenter.quest.QuestObjective import QuestObjective
from com.ankamagames.dofus.misc.utils.GameDataQuery import GameDataQuery
from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Logger import Logger


class Achievement(IDataCenter):

    logger = Logger("pyd2bot")

    MODULE: str = "Achievements"

    _totalAchievementPoints: float = None

    id: int

    nameId: int

    categoryId: int

    descriptionId: int

    iconId: int

    points: int

    level: int

    order: int

    accountLinked: bool

    objectiveIds: list[int]

    rewardIds: list[int]

    _name: str

    _desc: str

    _category: AchievementCategory

    _currentLevelRewards: AchievementRewardsWrapper

    _currentLevelRewardsAll: AchievementRewardsWrapper

    _currentRewardsCriteriaRespected: list[GroupItemCriterion]

    _currentRewardsCriteriaNotRespected: list[GroupItemCriterion]

    def __init__(self):
        super().__init__()

    @classmethod
    def getAchievementById(cls, id: int) -> "Achievement":
        return GameData.getObject(cls.MODULE, id)

    @classmethod
    def getAchievements(cls) -> list["Achievement"]:
        return GameData.getObjects(cls.MODULE)

    def getTotalAchievementPoints(self) -> float:
        achievements: list["Achievement"] = None
        if self._totalAchievementPoints is None:
            self._totalAchievementPoints = 0
            achievements = self.getAchievements()
            for achievement in achievements:
                if achievement.category.visible:
                    self._totalAchievementPoints += achievement.points
        return self._totalAchievementPoints

    @property
    def name(self) -> str:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name

    @property
    def description(self) -> str:
        rawText: str = None
        if self._desc == None:
            rawText = I18n.getText(self.descriptionId)
            self._desc = re.sub("[\s*challenge\s*,\s*(\d+)\s*]", repl, rawText, flags=re.MULTILINE)

            def repl(match):
                challengeId = float(match)
                if challengeId is None:
                    return "???"
                challenge = Challenge.getChallengeById(challengeId)
                if challenge == None:
                    return "???"
                return challenge.name

        return self._desc

    # def getDescriptionWithLinks(self, linkColor:str = "0xFFFFFF", hoverColor:str = "0xFFFFFF") -> str:
    #     return HyperlinkShowChallengeManager.parseChallengeLinks(I18n.getText(self.descriptionId), linkColor, hoverColor)

    @property
    def category(self) -> AchievementCategory:
        if not self._category:
            self._category = AchievementCategory.getAchievementCategoryById(self.categoryId)
        return self._category

    @property
    def canBeStarted(self) -> bool:
        ach: Achievement = None
        objId: int = 0
        achObj: AchievementObjective = None
        achObjValue: list = None
        qu: Quest = None
        quObj: QuestObjective = None
        questsIds: list[int] = None
        for objId in self.objectiveIds:
            achObj = AchievementObjective.getAchievementObjectiveById(objId)
            if achObj:
                achObjValue = achObj.criterion[:3].split(",")
                if achObj.criterion.find("PL") == 0:
                    return LevelItemCriterion(achObj.criterion).isRespected
                if achObj.criterion.find("Pl") == 0:
                    return PrestigeLevelItemCriterion(achObj.criterion).isRespected
                if achObj.criterion.find("OA") == 0:
                    ach = self.getAchievementById(int(achObjValue[0]))
                    if not ach.canBeStarted:
                        return False
                elif achObj.criterion.find("Q") == 0:
                    if achObj.criterion[1] == "o":
                        quObj = QuestObjective.getQuestObjectiveById(int(achObjValue[0]))
                        questsIds = GameDataQuery.queryEquals(Quest, "stepIds", quObj.stepId)
                        if len(questsIds) > 0:
                            qu = Quest.getQuestById(questsIds[0])
                    else:
                        qu = Quest.getQuestById(int(achObjValue[0]))
                    if not qu or not qu.canBeStarted:
                        return False
        return True

    def getKamasReward(self, pPlayerLevel: int) -> float:
        self.initCurrentLevelRewards(pPlayerLevel)
        return (
            0.0 if self._currentLevelRewards is None else float(self._currentLevelRewards.getKamasReward(pPlayerLevel))
        )

    def getExperienceReward(self, pPlayerLevel: int, pXpBonus: int) -> float:
        self.initCurrentLevelRewards(pPlayerLevel)
        return (
            0.0
            if self._currentLevelRewards is None
            else float(self._currentLevelRewards.getExperienceReward(pPlayerLevel, pXpBonus))
        )

    def getAchievementRewardByLevel(
        self, playerLevel: int, showAllReward: bool = False
    ) -> "AchievementRewardsWrapper":
        self.initCurrentLevelRewards(playerLevel)
        if showAllReward:
            return self._currentLevelRewardsAll
        return self._currentLevelRewards

    def initCurrentLevelRewards(self, level: int) -> None:
        criterion: GroupItemCriterion = None
        rewardId: int = 0
        characterRewardsTruncated: bool = False
        rewards: AchievementReward = None
        criterionToCheckForOb: IItemCriterion = None
        indexOperatorToRemove: int = 0
        index: int = 0
        criteriaListWithoutOb: list[IItemCriterion] = None
        conditionsWithoutOb: GroupItemCriterion = None
        operators: list[str] = None
        if self._currentRewardsCriteriaRespected == None:
            self._currentRewardsCriteriaRespected = list[GroupItemCriterion]()
        if self._currentRewardsCriteriaNotRespected == None:
            self._currentRewardsCriteriaNotRespected = list[GroupItemCriterion]()
        changeInCriteriaRespect: bool = False
        for criterion in self._currentRewardsCriteriaRespected:
            if not criterion.isRespected:
                changeInCriteriaRespect = True
        if not changeInCriteriaRespect:
            for criterion in self._currentRewardsCriteriaNotRespected:
                if criterion.isRespected:
                    changeInCriteriaRespect = True
        if not changeInCriteriaRespect and self._currentLevelRewards != None:
            return
        currentRewards: list[AchievementReward] = list[AchievementReward]()
        currentRewardsAll: list[AchievementReward] = list[AchievementReward]()
        self._currentRewardsCriteriaRespected = list[GroupItemCriterion]()
        self._currentRewardsCriteriaNotRespected = list[GroupItemCriterion]()
        for rewardId in self.rewardIds:
            rewards = AchievementReward.getAchievementRewardById(rewardId)
            if rewards.conditions == None:
                currentRewards.append(rewards)
                currentRewardsAll.append(rewards)
            else:
                if rewards.conditions.isRespected:
                    currentRewards.append(rewards)
                indexOperatorToRemove = -1
                index = 0
                criteriaListWithoutOb = list[IItemCriterion]()
                for criterionToCheckForOb in rewards.conditions.criteria:
                    if isinstance(criterionToCheckForOb, AchievementAccountItemCriterion):
                        indexOperatorToRemove = index - 1
                    else:
                        criteriaListWithoutOb.append(criterionToCheckForOb)
                    index += 1
                if len(criteriaListWithoutOb) > 0:
                    operators = rewards.conditions.operators
                    if indexOperatorToRemove > -1:
                        operators.splice(indexOperatorToRemove, 1)
                    conditionsWithoutOb = GroupItemCriterion.create(criteriaListWithoutOb, operators)
                if not conditionsWithoutOb or conditionsWithoutOb.isRespected:
                    currentRewardsAll.append(rewards)
            if rewards.conditions:
                if rewards.conditions.isRespected:
                    self._currentRewardsCriteriaRespected.append(rewards.conditions)
                else:
                    self._currentRewardsCriteriaNotRespected.append(rewards.conditions)
        characterRewardsTruncated = False
        if currentRewardsAll and (not currentRewards or len(currentRewards) < len(currentRewardsAll)):
            characterRewardsTruncated = True
        if not self._currentLevelRewards:
            self._currentLevelRewards = AchievementRewardsWrapper.create(
                currentRewards, self.id, characterRewardsTruncated
            )
        else:
            self._currentLevelRewards.update(currentRewards, characterRewardsTruncated)
        if not self._currentLevelRewardsAll:
            self._currentLevelRewardsAll = AchievementRewardsWrapper.create(currentRewardsAll, self.id)
        else:
            self._currentLevelRewardsAll.update(currentRewardsAll)

    idAccessors: IdAccessors = IdAccessors(getAchievementById, getAchievements)
