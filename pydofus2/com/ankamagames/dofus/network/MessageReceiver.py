import importlib
import json
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from pydofus2.com.ankamagames.jerakine.network.RawDataParser import RawDataParser
import pydofus2.com.ankamagames.dofus.Constants as Constants

with open(Constants.PROTOCOL_MSG_SHUFFLE_PATH, "r") as fp:
    msgShuffle: dict = json.load(fp)

_messages_to_discard = {
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
    "KnownZaapListMessage" "GuildGetInformationsMessage",
    "KnownZaapListMessage",
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
    "AlignmentRankUpdateMessage",
    "GameRolePlayArenaUpdatePlayerInfosAllQueuesMessage",
    "FollowedQuestsMessage",
    "CharacterExperienceGainMessage",
    "AccountHouseMessage",
    "EnabledChannelsMessage",
    "PrismsListUpdateMessage",
    "TrustStatusMessage",
    "NotificationListMessage",
    "AchievementListMessage",
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
    "LifePointsRegenBeginMessage",
    "MapFightCountMessage",
    "PartyUpdateMessage",
    "LifePointsRegenEndMessage",
    "CredentialsAcknowledgementMessage",
    "IdolFightPreparationUpdateMessage",
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
    "ChatSmileyMessage"
}

_messagesTypes = dict[int, type[NetworkMessage]]()
for cls_name, cls_infos in msgShuffle.items():
    if cls_name not in _messages_to_discard:
        modulePath = cls_infos["module"]
        try:
            clsModule = globals()[modulePath]
        except:
            clsModule = importlib.import_module(modulePath)
        cls = getattr(clsModule, cls_name)
        _messagesTypes[cls_infos["id"]] = cls


class MessageReceiver(RawDataParser, metaclass=ThreadSharedSingleton):
    def __init__(self):
        self.infight = False
        super().__init__()

    def parse(self, input: ByteArray, messageId: int, messageLength: int) -> INetworkMessage:
        messageType = _messagesTypes.get(messageId)
        if messageType:
            if messageType.__name__ == "GameFightJoinMessage":
                self.infight = True
            elif messageType.__name__ == "GameFightEndMessage":
                self.infight = False
        if not messageType or (
            Kernel()._mule
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

    @classmethod
    def getMsgNameById(cls, messageId: int) -> str:
        messageType = _messagesTypes.get(messageId)
        if not messageType:
            raise Exception(f"Unknown packet ID {messageId}")
        return messageType.__name__
