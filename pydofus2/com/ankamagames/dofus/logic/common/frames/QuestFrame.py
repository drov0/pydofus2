from types import FunctionType

import pydofus2.com.ankamagames.dofus.datacenter.quest.Quest as qst
from pydofus2.com.ankamagames.berilia.managers.KernelEvent import KernelEvent
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
    KernelEventsManager
from pydofus2.com.ankamagames.dofus.datacenter.world.MapPosition import \
    MapPosition
from pydofus2.com.ankamagames.dofus.internalDatacenter.quests.TreasureHuntWrapper import \
    TreasureHuntWrapper
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.network.enums.TreasureHuntDigRequestEnum import \
    TreasureHuntDigRequestEnum
from pydofus2.com.ankamagames.dofus.network.enums.TreasureHuntFlagRequestEnum import \
    TreasureHuntFlagRequestEnum
from pydofus2.com.ankamagames.dofus.network.enums.TreasureHuntRequestEnum import \
    TreasureHuntRequestEnum
from pydofus2.com.ankamagames.dofus.network.enums.TreasureHuntTypeEnum import \
    TreasureHuntTypeEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.achievement.AchievementListMessage import \
    AchievementListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestListMessage import \
    QuestListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestStartedMessage import \
    QuestStartedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestStepInfoMessage import \
    QuestStepInfoMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestValidatedMessage import \
    QuestValidatedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntDigRequestAnswerFailedMessage import \
    TreasureHuntDigRequestAnswerFailedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntDigRequestAnswerMessage import \
    TreasureHuntDigRequestAnswerMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntDigRequestMessage import \
    TreasureHuntDigRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntFinishedMessage import \
    TreasureHuntFinishedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntFlagRequestAnswerMessage import \
    TreasureHuntFlagRequestAnswerMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntFlagRequestMessage import \
    TreasureHuntFlagRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntMessage import \
    TreasureHuntMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.treasureHunt.TreasureHuntRequestAnswerMessage import \
    TreasureHuntRequestAnswerMessage
from pydofus2.com.ankamagames.dofus.network.types.game.achievement.AchievementAchieved import \
    AchievementAchieved
from pydofus2.com.ankamagames.dofus.network.types.game.achievement.AchievementAchievedRewardable import \
    AchievementAchievedRewardable
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayTreasureHintInformations import \
    GameRolePlayTreasureHintInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestActiveDetailedInformations import \
    QuestActiveDetailedInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestActiveInformations import \
    QuestActiveInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.quest.QuestObjectiveInformationsWithCompletion import \
    QuestObjectiveInformationsWithCompletion
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
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

    def treasureHuntFlagRequest(self, questType, index):
        thfrmsg = TreasureHuntFlagRequestMessage()
        thfrmsg.init(questType, index)
        ConnectionsHandler().send(thfrmsg)

    def treasureHuntDigRequest(self, questType):
        thdrmsg = TreasureHuntDigRequestMessage()
        thdrmsg.init(questType)
        ConnectionsHandler().send(thdrmsg)

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

    def getTreasureHunt(self, thtype) -> TreasureHuntWrapper:
        return self._treasureHunts.get(thtype)

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

    def processAchievements(self, b):
        # TODO: implement this method if needed
        pass
    
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
            KernelEventsManager().send(KernelEvent.QuestStart, msg)
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
                    for obj in questInfosDetailed.objectives:
                        if obj.objectiveStatus:
                            if obj.objectiveId not in self._activeObjectives:
                                if obj.objectiveId in self._completedObjectives:
                                    self._completedObjectives.remove(obj["objectiveId"])
                                self._activeObjectives.append(obj["objectiveId"])
                        elif obj.objectiveId not in self._completedObjectives:
                            if obj.objectiveId in self._activeObjectives:
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
                    break
            for qid in self._completedQuests:
                if qid == qsimsg.infos.questId:
                    questAlreadyInlist = True
                    break
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
                    self._questsInformations[stepsInfos.questId]["objectivesDialogParams"][objective.objectiveId] = (
                        [_ for _ in objective.dialogParams] if objective.dialogParams else []
                    )
                    if isinstance(objective, QuestObjectiveInformationsWithCompletion):
                        compl = {"current": objective.curCompletion, "max": objective.maxCompletion}
                        self._questsInformations[stepsInfos.questId]["objectivesData"][objective.objectiveId] = compl
                return True

            elif isinstance(qsimsg.infos, QuestActiveInformations):
                pass

            return True

        elif isinstance(msg, TreasureHuntMessage):
            self._treasureHunts[msg.questType] = TreasureHuntWrapper.create(
                msg.questType,
                msg.startMapId,
                msg.checkPointCurrent,
                msg.checkPointTotal,
                msg.totalStepCount,
                msg.availableRetryCount,
                msg.knownStepsList,
                msg.flags,
            )
            KernelEventsManager().send(KernelEvent.TreasureHuntUpdate, msg.questType)
            return True

        elif isinstance(msg, TreasureHuntRequestAnswerMessage):
            thramsg = msg
            treasureHuntRequestAnswerText = ""
            if thramsg.result == TreasureHuntRequestEnum.TREASURE_HUNT_ERROR_ALREADY_HAVE_QUEST:
                treasureHuntRequestAnswerText = I18n.getUiText("ui.treasureHunt.alreadyHaveQuest")
            elif thramsg.result == TreasureHuntRequestEnum.TREASURE_HUNT_ERROR_NO_QUEST_FOUND:
                treasureHuntRequestAnswerText = I18n.getUiText("ui.treasureHunt.noQuestFound")
            elif thramsg.result == TreasureHuntRequestEnum.TREASURE_HUNT_ERROR_UNDEFINED:
                treasureHuntRequestAnswerText = I18n.getUiText("ui.popup.impossible_action")
            elif thramsg.result == TreasureHuntRequestEnum.TREASURE_HUNT_ERROR_NOT_AVAILABLE:
                treasureHuntRequestAnswerText = I18n.getUiText("ui.treasureHunt.huntNotAvailable")
            elif thramsg.result == TreasureHuntRequestEnum.TREASURE_HUNT_ERROR_DAILY_LIMIT_EXCEEDED:
                treasureHuntRequestAnswerText = I18n.getUiText("ui.treasureHunt.huntLimitExceeded")
            if treasureHuntRequestAnswerText:
                Logger().warning(treasureHuntRequestAnswerText)
            KernelEventsManager().send(
                KernelEvent.TreasureHuntRequestAnswer, thramsg.result, treasureHuntRequestAnswerText
            )
            return True

        elif isinstance(msg, TreasureHuntFinishedMessage):
            thfmsg = msg
            if thfmsg.questType in self._treasureHunts:
                del self._treasureHunts[thfmsg.questType]
                KernelEventsManager().send(KernelEvent.TreasureHuntFinished, thfmsg.questType)
            return True

        elif isinstance(msg, TreasureHuntDigRequestAnswerFailedMessage):
            wrongFlagCount = int(msg.wrongFlagCount)
            msg.result = TreasureHuntDigRequestEnum(msg.result)
            if msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_ERROR_IMPOSSIBLE:
                treasureHuntDigAnswerText = I18n.getUiText("ui.fight.wrongMap")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_ERROR_UNDEFINED:
                treasureHuntDigAnswerText = I18n.getUiText("ui.popup.impossible_action")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_LOST:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.huntFail")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_NEW_HINT:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.stepSuccess")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_WRONG:
                if wrongFlagCount > 1:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digWrongFlags", [wrongFlagCount])
                elif wrongFlagCount > 0:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digWrongFlag")
                else:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digFail")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_WRONG_AND_YOU_KNOW_IT:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.noNewFlag")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_FINISHED:
                if msg.questType == TreasureHuntTypeEnum.TREASURE_HUNT_CLASSIC:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.huntSuccess")

            if treasureHuntDigAnswerText:
                Logger().info(treasureHuntDigAnswerText)
                KernelEventsManager().send(
                    KernelEvent.TreasureHuntDigAnswer, wrongFlagCount, msg.result, treasureHuntDigAnswerText
                )
            return True

        elif isinstance(msg, GameRolePlayTreasureHintInformations):
            KernelEventsManager().send(KernelEvent.TreasureHintInformation, msg.npcId)
            return True

        if isinstance(msg, TreasureHuntDigRequestAnswerMessage):
            wrongFlagCount = 0
            if isinstance(msg, TreasureHuntDigRequestAnswerFailedMessage):
                wrongFlagCount = msg.wrongFlagCount

            if msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_ERROR_IMPOSSIBLE:
                treasureHuntDigAnswerText = I18n.getUiText("ui.fight.wrongMap")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_ERROR_UNDEFINED:
                treasureHuntDigAnswerText = I18n.getUiText("ui.popup.impossible_action")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_LOST:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.huntFail")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_NEW_HINT:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.stepSuccess")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_WRONG:
                if wrongFlagCount > 1:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digWrongFlags", wrongFlagCount)
                elif wrongFlagCount > 0:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digWrongFlag")
                else:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.digFail")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_WRONG_AND_YOU_KNOW_IT:
                treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.noNewFlag")
            elif msg.result == TreasureHuntDigRequestEnum.TREASURE_HUNT_DIG_FINISHED:
                if msg.questType == TreasureHuntTypeEnum.TREASURE_HUNT_CLASSIC:
                    treasureHuntDigAnswerText = I18n.getUiText("ui.treasureHunt.huntSuccess")
            if treasureHuntDigAnswerText:
                Logger().info(treasureHuntDigAnswerText)
            KernelEventsManager().send(
                KernelEvent.TreasureHuntDigAnswer, msg.questType, msg.result, treasureHuntDigAnswerText
            )

            return True

        if isinstance(msg, TreasureHuntFlagRequestAnswerMessage):
            result = TreasureHuntFlagRequestEnum(msg.result)
            err = ""
            if result == TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_OK:
                pass
            elif result in [
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_ERROR_UNDEFINED,
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_WRONG,
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_TOO_MANY,
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_ERROR_IMPOSSIBLE,
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_WRONG_INDEX,
                TreasureHuntFlagRequestEnum.TREASURE_HUNT_FLAG_SAME_MAP,
            ]:
                err = f"Flag put request failed for reason : {result.name}"
            if err:
                Logger().error(err)
            KernelEventsManager().send(
                KernelEvent.TreasureHuntFlagRequestAnswer, result, err
            )
            return True
        return False  # or whatever the default return value should be

    def pulled(self) -> bool:
        return True

    def hasTreasureHunt(self) -> bool:
        key = None
        for key in self._treasureHunts:
            if key != None:
                return True
        return False
