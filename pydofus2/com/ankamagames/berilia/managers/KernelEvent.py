from enum import Enum, auto


class KernelEvent(Enum):
    # Common
    ReloginToken = auto()
    MovementRequestRejected = auto()
    ServersList = auto()
    CharactersList = auto()
    ClientCrashed = auto()
    PlayerLoggedIn = auto()
    PlayerInGameReady = auto()
    PlayerDead = auto()
    PlayerAlive = auto()
    CharacterSelectedSuccessfully = auto()
    ClientShutdown = auto()
    ClientRestart = auto()
    MapLoaded = auto()
    MapDataProcessed = auto()
    FramePushed = auto()
    FramePulled = auto()
    ClientReconnect = auto()
    ClientClosed = auto()
    TextInformation = auto()

    
    # Fight
    FightSwordShowed = auto()
    FightResumed = auto()
    FighterMovementApplied = auto()
    FighterCastedSpell = auto()
    SequenceExecFinished = auto()
    FightStarted = auto()
    FightEnded = auto()
    MuleFightContext = auto()
    FighterShowed = auto()
    FightJoined = auto()
    RoleplayStarted = auto()
    
    # Interactives
    IElemBeingUsed = auto()
    InteractiveElementUsed = auto()
    InteractiveUseError = auto()
    
    # cell movement

    # Entities movement
    EntityMoving = auto()
    EntityVanished = auto()
    InactivityWarning = auto()
    ActorShowed = auto()
    CurrentMap = auto()
    PlayerMovementCompleted = auto()
    
    # Player updates
    CharacterStats = auto()
    PlayerLeveledUp = auto()
    PlayerPodsFull = auto()
    PlayerStateChanged = auto()
    InventoryWeightUpdate = auto()
    StatsUpgradeResult = auto()
    ObtainedItem = auto()
    
    # NPC
    NpcDialogOpen = auto()
    NpcQuestion = auto()
    
    # Parties
    CharacterNameSuggestion = auto()
    CharacterNameSuggestionFailed = auto()
    CharacterCreationResult = auto()
    DialogLeft = auto()
    ExchangeClose = auto()
    QuestStart = auto()
    CharacterDelPrepare = auto()
    ServerTextInfo = auto()
    
    # Party
    IJoinedParty = auto()
    MemberJoinedParty = auto()
    MemberLeftParty = auto()
    PartyDeleted = auto()
    PartyInvitation = auto()
    PartyMemberStartedFight = auto()
    PartyJoinFailed = auto()
    PartyInviteCancel = auto()
    KamasUpdate = auto()
    InteractiveElemUpdate = auto()
    
    # exchange events
    ExchangeRequestFromMe = auto()
    ExchangeRequestToMe = auto()
    ExchangeStartOkNpcTrade = auto()
    ExchangeStartedType = auto()
    ExchangeStartOkRunesTrade = auto()
    ExchangeStartOkRecycleTrade = auto()
    ExchangeObjectListModified = auto()
    ExchangeObjectAdded = auto()
    ExchangeObjectListAdded = auto()
    ExchangeObjectRemoved = auto()
    ExchangeObjectListRemoved = auto()
    ExchangeObjectModified = auto()
    ExchangeBankStartedWithStorage = auto()
    ExchangeBankStartedWithMultiTabStorage = auto()
    ExchangeStarted = auto()
    ExchangeBankStarted = auto()
    ExchangeStartOkNpcShop = auto()
    RecycleResult = auto()
    GuildChestTabContribution = auto()
    GuildChestContributions = auto()
    ExchangeLeave = auto()
    ExchangeIsReady = auto()
    ExchangeKamaModified = auto()
    ExchangePodsModified = auto()
    
    # teleport events
    TeleportDestinationList = auto()
    
    # pvp
    AlignmentRankUpdate = auto()
    CharacterAlignmentWarEffortProgressionHook = auto()
    UpdateWarEffortHook = auto()
    AlignmentWarEffortProgressionMessageHook = auto()
    
    # inventory 
    ObjectAdded = auto()
    InventoryContent = auto()
    
    # job
    JobLevelUp = auto()
    
    # quest
    TreasureHuntUpdate = auto()
    TreasureHuntRequestAnswer = auto()
    TreasureHuntFinished = auto()
    TreasureHuntDigAnswer = auto()
    TreasureHintInformation = auto()
    TreasureHuntFlagRequestAnswer = auto()