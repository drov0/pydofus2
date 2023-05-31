from enum import Enum


class KernelEvent(Enum):
    # common
    RELOGIN_TOKEN = 37
    MOVE_REQUEST_REJECTED = 0
    SERVERS_LIST = 1
    CHARACTERS_LIST = 2
    CRASH = 3
    LOGGED_IN = 4
    IN_GAME = 5
    DEAD = 6
    ALIVE = 7
    CHARACTER_SELECTION_SUCCESS = 9
    SHUTDOWN = 10
    RESTART = 11
    MAPLOADED = 12
    MAPPROCESSED = 13
    FRAME_PUSHED = 14
    FRAME_PULLED = 15
    RECONNECT = 16
    CONNECTION_CLOSED = -2
    # fight
    FIGHT_SWORD_SHOWED = 50
    FIGHT_RESUMED = 17
    FIGHTER_MOVEMENT_APPLIED = 18
    FIGHTER_CASTED_SPELL = 19
    SEQUENCE_EXEC_FINISHED = 20
    FIGHT_STARTED = 24
    FIGHT_ENDED = 30
    MULE_FIGHT_CONTEXT = 52
    FIGHTER_SHOWED = -5
    FIGHT_JOINED = -6
    # phenix
    PHENIX_AUTO_REVIVE_ENDED = 21
    AUTO_TRIP_ENDED = 22
    INVENTORY_UNLOADED = 23
    ROLEPLAY_STARTED = -1
    # interactives
    INTERACTIVE_ELEMENT_BEING_USED = 25
    INTERACTIVE_ELEMENT_USED = 26
    INTERACTIVE_USE_ERROR = 27
    # cell movement

    # entities movement
    ENTITY_MOVING = 29
    ENTITY_VANISHED = 31
    INACTIVITY_WARNING = 34
    ACTORSHOWED = 8
    CURRENT_MAP = 51
    PLAYER_MOVEMENT_COMPLETED = -6
    # player updates
    CHARACTER_STATS = 36
    LEVEL_UP = 35
    FULL_PODS = 32
    PLAYER_STATE_CHANGED = 28
    INVENTORY_WEIGHT_UPDATE = 42
    # NPC
    NPC_DIALOG_OPEN = 40
    NPC_QUESTION = 41
    # Parties
    CHARACTER_NAME_SUGGESTION = 38
    CHARACTER_NAME_SUGGESTION_FAILED = 46
    CHARACTER_CREATION_RESULT = 39
    DIALOG_LEFT = 43
    EXCHANGE_CLOSE = 45
    QUEST_START = 47
    CHAR_DEL_PREP = 48
    TEXT_INFO = 49
    # Party
    IJoinedParty = 53
    MemberJoinedParty = 54
    MemberLeftParty = 55
    PartyDeleted = 56
    PartyInvitation = 57
    PartyMemberStartedFight = 58
    PartyJoinFailed = 59
    PartyInviteCancel = 60
    KamasUpdate = 61
    IinteractiveElemUpdate = 62
    # exchange events
    ExchangeRequestFromMe = 63
    ExchangeRequestToMe = 64
    ExchangeStartOkNpcTrade = 65
    ExchangeStartedType = 66
    ExchangeStartOkRunesTrade = 67
    ExchangeStartOkRecycleTrade = 68
    ExchangeObjectListModified = 69
    ExchangeObjectAdded = 70
    ExchangeObjectListAdded = 71
    ExchangeObjectRemoved = 72
    ExchangeObjectListRemoved = 73
    ExchangeObjectModified = 74
    ExchangeBankStartedWithStorage = 75
    ExchangeBankStartedWithMultiTabStorage = 76
    ExchangeStarted = 77
    ExchangeBankStarted = 78
    TextInformation = 79
    ExchangeStartOkNpcShop = 80
    RecycleResult = 81
    GuildChestTabContribution = 82
    GuildChestContributions = 83
    ExchangeLeave = 84
    ExchangeIsReady = 85
    ExchangeKamaModified = 86
    ExchangePodsModified = 87
    # teleport events
    TeleportDestinationList = 88
    # pvp
    AlignmentRankUpdate = 89
    CharacterAlignmentWarEffortProgressionHook = 90
    UpdateWarEffortHook = 91
    AlignmentWarEffortProgressionMessageHook = 92
    # inventory 
    ObjectAdded = 93
    InventoryContent = 95
    
    # job
    JobLevelUp = 94