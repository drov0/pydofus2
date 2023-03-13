from types import FunctionType
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import KernelEvent, KernelEventsManager
import pydofus2.com.ankamagames.dofus.datacenter.quest.Quest as qst
from pydofus2.com.ankamagames.dofus.network.messages.game.achievement.AchievementListMessage import (
    AchievementListMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestListMessage import (
    QuestListMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestStartedMessage import QuestStartedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestStepInfoMessage import (
    QuestStepInfoMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestValidatedMessage import (
    QuestValidatedMessage,
)
from pydofus2.com.ankamagames.dofus.network.types.game.achievement.AchievementAchieved import AchievementAchieved
from pydofus2.com.ankamagames.dofus.network.types.game.achievement.AchievementAchievedRewardable import (
    AchievementAchievedRewardable,
)
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestActiveDetailedInformations import (
    QuestActiveDetailedInformations,
)
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestActiveInformations import (
    QuestActiveInformations,
)
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestObjectiveInformationsWithCompletion import (
    QuestObjectiveInformationsWithCompletion,
)
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class QuestFrame(Frame):

    FIRST_TEMPORIS_REWARD_ACHIEVEMENT_ID: int = 2903

    FIRST_TEMPORIS_COMPANION_REWARD_ACHIEVEMENT_ID: int = 2906

    TEMPORIS_CATEGORY: int = 107

    STORAGE_NEW_TEMPORIS_REWARD: str = "storageNewTemporisReward"

    notificationList: list

    _nbAllAchievements: int

    _activeQuests: list[QuestActiveInformations]

    _completedQuests: list[int]

    _reinitDoneQuests: list[int]

    _followedQuests: list[int]

    _questsInformations: dict

    _finishedAchievements: list[AchievementAchieved]

    _activeObjectives: list[int]

    _completedObjectives: list[int]

    _finishedAccountAchievementIds: list

    _finishedCharacterAchievementIds: list

    _rewardableAchievements: list[AchievementAchievedRewardable]

    _rewardableAchievementsVisible: bool

    _treasureHunts: dict

    _flagColors: list

    _followedQuestsCallback: FunctionType

    _achievementsFinishedCache: list = None

    _achievementsList: AchievementListMessage

    _achievementsListProcessed: bool = False

    def __init__(self):
        self._followedQuests = list[int]()
        self._questsInformations = dict()
        self._activeObjectives = list[int]()
        self._completedObjectives = list[int]()
        self._treasureHunts = dict()
        self._flagColors = list()
        super().__init__()

    @property
    def achievmentsList(self) -> AchievementListMessage:
        return self._achievementsList

    @property
    def achievmentsListProcessed(self) -> bool:
        return self._achievementsListProcessed

    @achievmentsListProcessed.setter
    def achievmentsListProcessed(self, value: bool):
        self._achievementsListProcessed = value

    @property
    def followedQuestsCallback(self) -> FunctionType:
        return self._followedQuestsCallback

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    @property
    def finishedAchievements(self) -> list[AchievementAchieved]:
        return self._finishedAchievements

    @property
    def finishedAccountAchievementIds(self) -> list:
        return self._finishedAccountAchievementIds

    @property
    def finishedCharacterAchievementIds(self) -> list:
        return self._finishedCharacterAchievementIds

    def getActiveQuests(self) -> list[QuestActiveInformations]:
        return self._activeQuests

    def getCompletedQuests(self) -> list[int]:
        return self._completedQuests

    def getReinitDoneQuests(self) -> list[int]:
        return self._reinitDoneQuests

    def getFollowedQuests(self) -> list[int]:
        return self._followedQuests

    def getQuestInformations(self, questId: int) -> dict:
        return self._questsInformations[questId]

    def getActiveObjectives(self) -> list[int]:
        return self._activeObjectives

    def getCompletedObjectives(self) -> list[int]:
        return self._completedObjectives

    @property
    def rewardableAchievements(self) -> list[AchievementAchievedRewardable]:
        return self._rewardableAchievements

    def pushed(self) -> bool:
        self._rewardableAchievements = list[AchievementAchievedRewardable]()
        self._finishedAchievements = list[AchievementAchieved]()
        self._finishedAccountAchievementIds = list()
        self._finishedCharacterAchievementIds = list()
        self._treasureHunts = dict()
        self._achievementsList = AchievementListMessage()
        self._achievementsList.init(list[AchievementAchieved]())
        return True

    def process(self, msg: Message) -> bool:
        if isinstance(msg, QuestValidatedMessage):
            qvmsg = msg
            if not self._completedQuests:
                self._completedQuests = list[int]()
            else:
                index = 0
                for activeQuest in self._activeQuests:
                    if activeQuest.questId == qvmsg.questId:
                        del self._activeQuests[index]
                        break
            self._completedQuests.append(qvmsg.questId)
            questValidated = qst.Quest.getQuestById(qvmsg.questId)
            if not questValidated:
                return True
            for step in questValidated.steps:
                for questStepObjId in step.objectiveIds:
                    if questStepObjId not in self._completedObjectives:
                        if questStepObjId in self._activeObjectives:
                            self._activeObjectives.remove(questStepObjId)
                        self._completedObjectives.append(questStepObjId)
            return True

        elif isinstance(msg, QuestStartedMessage):
            KernelEventsManager().send(KernelEvent.QUEST_START, msg)
            return True

        elif isinstance(msg, QuestListMessage):
            qlmsg = msg
            self._activeQuests = qlmsg.activeQuests
            self._completedQuests = qlmsg.finishedQuestsIds
            self._completedQuests = self._completedQuests + qlmsg.reinitDoneQuestsIds
            self._reinitDoneQuests = qlmsg.reinitDoneQuestsIds
            self._activeObjectives = list[int]()
            self._completedObjectives = list[int]()
            for questInfosDetailed in self._activeQuests:
                if questInfosDetailed:
                    for obj in questInfosDetailed["objectives"]:
                        if obj["objectiveStatus"]:
                            if obj["objectiveId"] not in self._activeObjectives:
                                if obj["objectiveId"] in self._completedObjectives:
                                    self._completedObjectives.remove(obj["objectiveId"])
                                self._activeObjectives.append(obj["objectiveId"])
                        elif obj["objectiveId"] not in self._completedObjectives:
                            if obj["objectiveId"] in self._activeObjectives:
                                self._activeObjectives.remove(obj["objectiveId"])
                            self._completedObjectives.append(obj["objectiveId"])
            for id in self._completedQuests:
                quest = qst.Quest.getQuestById(id)
                if quest:
                    steps = quest.steps
                    for qs in steps:
                        self._completedObjectives = self._completedObjectives.extend(qs.objectiveIds)
            return True

        elif isinstance(msg, QuestStepInfoMessage):
            qsimsg = msg
            questAlreadyInlist = False
            for qai in self._activeQuests:
                if qai.questId == qsimsg.infos.questId:
                    questAlreadyInlist = True
            for qid in self._completedQuests:
                if qid == qsimsg.infos.questId:
                    questAlreadyInlist = True
            if not questAlreadyInlist:
                self._activeQuests.append(qsimsg.infos)
            if isinstance(qsimsg.infos, QuestActiveDetailedInformations):
                stepsInfos: "QuestActiveDetailedInformations" = qsimsg.infos
                self._questsInformations[stepsInfos.questId] = {
                    "questId": stepsInfos.questId,
                    "stepId": stepsInfos.stepId,
                }
                self._questsInformations[stepsInfos.questId]["objectives"] = dict()
                self._questsInformations[stepsInfos.questId]["objectivesData"] = list()
                self._questsInformations[stepsInfos.questId]["objectivesDialogParams"] = list()
                for objective in stepsInfos.objectives:
                    if objective.objectiveStatus:
                        if objective.objectiveId not in self._activeObjectives:
                            if objective.objectiveId in self._completedObjectives:
                                self._completedObjectives.remove(objective.objectiveId)
                            self._activeObjectives.append(objective.objectiveId)
                    elif objective.objectiveId not in self._completedObjectives:
                        if objective.objectiveId in self._activeObjectives:
                            self._activeObjectives.remove(objective.objectiveId)
                        self._completedObjectives.append(objective.objectiveId)
                    self._questsInformations[stepsInfos.questId]["objectives"][
                        objective.objectiveId
                    ] = objective.objectiveStatus
                    if objective.dialogParams and len(objective.dialogParams) > 0:
                        dialogParams = list()
                        nbParams = len(objective.dialogParams)
                        for i in range(nbParams):
                            dialogParams.append(objective.dialogParams[i])
                    self._questsInformations[stepsInfos.questId]["objectivesDialogParams"][
                        objective.objectiveId
                    ] = dialogParams
                    if isinstance(objective, QuestObjectiveInformationsWithCompletion):
                        compl = {}
                        compl.current = objective.curCompletion
                        compl.max = objective.maxCompletion
                        self._questsInformations[stepsInfos.questId]["objectivesData"][objective.objectiveId] = compl
            elif isinstance(qsimsg.infos, QuestActiveInformations):
                pass
            return True

    def pulled(self) -> bool:
        return True

    def hasTreasureHunt(self) -> bool:
        key = None
        for key in self._treasureHunts:
            if key != None:
                return True
        return False
