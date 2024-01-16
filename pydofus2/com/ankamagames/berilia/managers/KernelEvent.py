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
    SelectedServerData = auto()
    ServerStatusUpdate = auto()
    SelectedServerRefused = auto()
    
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
    FightLeader = auto()
    
    # buffs in fight
    BuffAdd = auto()
    BuffUpdate = auto()
    
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
    JobExperienceUpdate = auto()
    PlayerAddedToSceene = auto()
    
    # NPC
    NpcDialogOpen = auto()
    NpcQuestion = auto()
    
    # Parties
    CharacterNameSuggestion = auto()
    CharacterNameSuggestionFailed = auto()
    CharacterCreationResult = auto()
    ExchangeClose = auto()
    QuestStart = auto()
    CharacterDelPrepare = auto()
    ServerTextInfo = auto()
    
    # Party
    IJoinedParty = auto()
    MemberJoinedParty = auto()
    MemberLeftParty = auto()
    PartyDeleted = auto()
    PartyInvited = auto()
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
    InHavenBag = auto()
    
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
    JobAllowMultiCraftRequest = auto()
    
    # quest
    TreasureHuntUpdate = auto()
    TreasureHuntRequestAnswer = auto()
    TreasureHuntFinished = auto()
    TreasureHuntDigAnswer = auto()
    TreasureHintInformation = auto()
    TreasureHuntFlagRequestAnswer = auto()
    
    # Challenges
    ChallengeListUpdate = auto()
    CloseChallengeProposal = auto()
    ChallengeTargetUpdate = auto()
    ChallengeResult = auto()
    ChallengeModSelected = auto()
    ChallengeBonusSelected = auto()
    
    # achievements
    AchievementRewardSuccess = auto()
    RewardableAchievementsVisible = auto()
    
    # Mount 
    MountSterilized = auto()
    MountStableUpdate = auto()
    MountRenamed = auto()
    MountXpRatio = auto()
    CertificateMountData = auto()
    PaddockedMountData = auto()
    MountRiding = auto()
    MountReleased = auto()
    MountSet = auto()
    MountUnSet = auto()
    ExchangeWeight = auto()
    MountEquipedError = auto()
    ExchangeStartOkMount = auto()
    
    # social
    GuildInvited = auto()
    LeaveDialog = auto()
    PlayerStatusUpdate = auto()