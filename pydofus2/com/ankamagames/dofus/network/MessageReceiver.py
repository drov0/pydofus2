import importlib
import json

import pydofus2.com.ankamagames.dofus.Constants as Constants
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import \
    NetworkMessage
from pydofus2.com.ankamagames.jerakine.network.RawDataParser import \
    RawDataParser

with open(Constants.PROTOCOL_MSG_SHUFFLE_PATH, "r") as fp:
    msgShuffle: dict = json.load(fp)

_discardMessages = True
_messages_to_discard = {
    "ServerSettingsMessage",
    "SetCharacterRestrictionsMessage",
    "GameContextRefreshEntityLookMessage",
    "ChatServerMessage",
    "ChatServerWithObjectMessage",
    "UpdateMapPlayersAgressableStatusMessage",
    "BasicAckMessage",
    "BasicNoOperationMessage",
    "ListMapNpcsQuestStatusUpdateMessage",
    "GameMapChangeOrientationMessage",
    "HousePropertiesMessage",
    "GuildGetInformationsMessage",
    "PrismsListMessage",
    "ChatCommunityChannelCommunityMessage",
    "FriendWarnOnConnectionStateMessage",
    "FriendWarnOnLevelGainStateMessage",
    "FriendGuildWarnOnAchievementCompleteStateMessage",
    "WarnOnPermaDeathStateMessage",
    "FriendStatusShareStateMessage",
    "GuildMemberWarnOnConnectionStateMessage",
    "ServerExperienceModificatorMessage",
    "SpouseStatusMessage",
    "IdolListMessage",
    "AlmanachCalendarDateMessage",
    "CharacterCapabilitiesMessage",
    "ShortcutBarContentMessage",
    "AlterationsMessage",
    "HavenBagRoomUpdateMessage",
    "HavenBagPackListMessage",
    "StartupActionsListMessage",
    "EmoteListMessage",
    "JobCrafterDirectorySettingsMessage",
    "EnabledChannelsMessage" "ServerSettingsMessage",
    "ServerOptionalFeaturesMessage",
    "ServerSessionConstantsMessage",
    "AccountCapabilitiesMessage",
    "GameRolePlayArenaUpdatePlayerInfosAllQueuesMessage",
    "FollowedQuestsMessage",
    "CharacterExperienceGainMessage",
    "AccountHouseMessage",
    "EnabledChannelsMessage",
    "PrismsListUpdateMessage",
    "TrustStatusMessage",
    "NotificationListMessage",
    "ChallengeInfoMessage",
    "ChallengeTargetUpdateMessage",
    "ChallengeResultMessage",
    "ChallengeTargetsListMessage",
    "GameFightSpectateMessage",
    "GameFightSpectatorJoinMessage",
    "EmotePlayMessage",
    "PartyFollowStatusUpdateMessage",
    "PartyUpdateLightMessage",
    "PartyRestrictedMessage",
    "PartyLeaderUpdateMessage",
    "MapFightCountMessage",
    "PartyUpdateMessage",
    "CredentialsAcknowledgementMessage",
    "IdolFightPreparationUpdateMessage",
    "SubareaRewardRateMessage",
    "LifePointsRegenEndMessage",
    "LifePointsRegenBeginMessage",
    "TitlesAndOrnamentsListMessage",
    "GameRolePlayArenaRegistrationStatusMessage",
    "PrismAddOrUpdateMessage",
    "HavenBagPermissionsUpdateMessage",
    "HavenBagFurnituresMessage",
    "PaddockPropertiesMessage",
    "GameDataPaddockObjectListAddMessage",
}

_mule_fight_messages_to_discard = {
    "GameActionFightDispellableEffectMessage",
    "GameActionUpdateEffectTriggerCountMessage",
    "GameEntitiesDispositionMessage",
    "GameFightPlacementPossiblePositionsMessage",
    "GameFightTurnListMessage",
    "SequenceEndMessage",
    "GameFightJoinMessage",
    "GameFightTurnStartMessage",
    "GameFightOptionStateUpdateMessage",
    "GameFightTurnEndMessage",
    "GameActionFightLifePointsLostMessage",
    "GameFightHumanReadyStateMessage",
    "GameFightNewRoundMessage",
    "CharacterStatsListMessage",
    "SequenceStartMessage",
    "GameFightStartMessage",
    "GameActionFightDeathMessage",
    "RefreshCharacterStatsMessage",
    "GameFightShowFighterMessage",
    "GameFightSynchronizeMessage",
    "GameActionFightPointsVariationMessage",
    "GameActionFightSpellCastMessage",
    "GameFightUpdateTeamMessage",
    "GameMapMovementMessage",
    "GameFightPlacementPossiblePositionsMessage",
    "GameFightShowFighterMessage",
    "CharacterStatsListMessage",
    "MapComplementaryInformationsDataMessage",
    "GameActionFightInvisibilityMessage",
    "GameFightRefreshFighterMessage",
    "GameActionFightDodgePointLossMessage",
    "GameActionFightLifePointsLostMessage",
    "ChatSmileyMessage",
}

_messagesTypes = dict[int, type[NetworkMessage]]()
for cls_name, cls_infos in msgShuffle.items():
    if _discardMessages and cls_name not in _messages_to_discard:
        modulePath = cls_infos["module"]
        try:
            clsModule = globals()[modulePath]
        except:
            clsModule = importlib.import_module(modulePath)
        cls = getattr(clsModule, cls_name)
        _messagesTypes[cls_infos["id"]] = cls


class MessageReceiver(RawDataParser, metaclass=Singleton):
    
    def __init__(self, discard=True):
        self.infight = False
        self.discard = discard
        self.msgLenLen = None
        self.msgLen = None
        self.msgId = None
        super().__init__()

    def parseMessage(self, input: ByteArray, messageId: int, messageLength: int) -> NetworkMessage:
        messageType = _messagesTypes.get(messageId)
        if self.discard:
            if messageType:
                if messageType.__name__ == "GameFightJoinMessage":
                    self.infight = True
                    Logger().separator("Fight started", "+")
                elif messageType.__name__ == "GameFightEndMessage":
                    self.infight = False
                    Logger().separator("Fight ended", "-")
        if not messageType or (
            self.discard
            and Kernel().isMule
            and self.infight
            and messageType.__name__ in _mule_fight_messages_to_discard
        ):
            message = NetworkMessage()
            message.unpacked = False
            input.position += messageLength
            return message
        message = messageType.unpack(input, messageLength)
        message.unpacked = True
        return message

    def parse(self, buffer: ByteArray, callback, from_client=False):
        while buffer.remaining():
            if self.msgLenLen is None:
                if buffer.remaining() < 2:
                    break
                staticHeader = buffer.readUnsignedShort()
                self.msgId = staticHeader >> NetworkMessage.PACKET_ID_RIGHT_SHIFT
                self.msgLenLen = staticHeader & NetworkMessage.BIT_MASK
            if from_client and self.msgCount is None:
                if buffer.remaining() < 4:
                    break
                self.msgCount = buffer.readUnsignedInt()
            if self.msgLen is None:
                if buffer.remaining() < self.msgLenLen:
                    break
                self.msgLen = int.from_bytes(buffer.read(self.msgLenLen), "big")
            if buffer.remaining() < self.msgLen:
                break
            msg_bytes = buffer.read(self.msgLen)
            msg = self.parseMessage(msg_bytes, self.msgId, self.msgLen)
            self.msgId = None
            self.msgLenLen = None
            self.msgLen = None
            self.msgCount = None
            buffer.trim()
            callback(msg)
        
        
    @classmethod
    def getMsgNameById(cls, messageId: int) -> str:
        messageType = _messagesTypes.get(messageId)
        if not messageType:
            Logger().warning(f"Unknown packet ID {messageId}")
            return None
        return messageType.__name__
