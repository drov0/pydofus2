import math
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
import com.ankamagames.atouin.managers.MapDisplayManager as mdm
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.datacenter.monsters.Companion import Companion
from com.ankamagames.dofus.datacenter.monsters.Monster import Monster
from com.ankamagames.dofus.datacenter.npcs.TaxCollectorFirstname import (
    TaxCollectorFirstname,
)
from com.ankamagames.dofus.datacenter.npcs.TaxCollectorName import TaxCollectorName
import com.ankamagames.dofus.datacenter.spells.Spell as spellmod
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from com.ankamagames.dofus.internalDatacenter.fight.FightResultEntryWrapper import (
    FightResultEntryWrapper,
)
from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.internalDatacenter.world.WorldPointWrapper import (
    WorldPointWrapper,
)
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from com.ankamagames.dofus.logic.game.common.frames.SpellInventoryManagementFrame import (
    SpellInventoryManagementFrame,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.messages.FightEndingMessage import (
    FightEndingMessage,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.actions.ChallengeTargetsListRequestAction import (
    ChallengeTargetsListRequestAction,
)
from com.ankamagames.dofus.logic.game.fight.actions.UpdateSpellModifierAction import (
    UpdateSpellModifierAction,
)
import com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper as fevth
from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import (
    FightBattleFrame,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightPreparationFrame import (
    FightPreparationFrame,
)
from com.ankamagames.dofus.logic.game.fight.managers.BuffManager import BuffManager
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import (
    CurrentPlayedFighterManager,
)
from com.ankamagames.dofus.logic.game.fight.managers.SpellModifiersManager import (
    SpellModifiersManager,
)
from com.ankamagames.dofus.logic.game.fight.types.CastingSpell import CastingSpell
from com.ankamagames.dofus.network.enums.CharacterSpellModificationTypeEnum import (
    CharacterSpellModificationTypeEnum,
)
from com.ankamagames.dofus.network.enums.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.FightOutcomeEnum import FightOutcomeEnum
from com.ankamagames.dofus.network.enums.FightTypeEnum import FightTypeEnum
from com.ankamagames.dofus.network.enums.MapObstacleStateEnum import (
    MapObstacleStateEnum,
)
from com.ankamagames.dofus.network.enums.TeamEnum import TeamEnum
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCarryCharacterMessage import (
    GameActionFightCarryCharacterMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightNoSpellCastMessage import (
    GameActionFightNoSpellCastMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import (
    GameContextDestroyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameContextReadyMessage import (
    GameContextReadyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightEndMessage import (
    GameFightEndMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightJoinMessage import (
    GameFightJoinMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightLeaveMessage import (
    GameFightLeaveMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightResumeMessage import (
    GameFightResumeMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightResumeWithSlavesMessage import (
    GameFightResumeWithSlavesMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightSpectateMessage import (
    GameFightSpectateMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightSpectatorJoinMessage import (
    GameFightSpectatorJoinMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightStartMessage import (
    GameFightStartMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightStartingMessage import (
    GameFightStartingMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightUpdateTeamMessage import (
    GameFightUpdateTeamMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.arena.ArenaFighterIdleMessage import (
    ArenaFighterIdleMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.arena.ArenaFighterLeaveMessage import (
    ArenaFighterLeaveMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.breach.BreachGameFightEndMessage import (
    BreachGameFightEndMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.challenge.ChallengeInfoMessage import (
    ChallengeInfoMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.challenge.ChallengeResultMessage import (
    ChallengeResultMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.challenge.ChallengeTargetUpdateMessage import (
    ChallengeTargetUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.challenge.ChallengeTargetsListMessage import (
    ChallengeTargetsListMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.challenge.ChallengeTargetsListRequestMessage import (
    ChallengeTargetsListRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapInstanceMessage import (
    CurrentMapInstanceMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapMessage import (
    CurrentMapMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapObstacleUpdateMessage import (
    MapObstacleUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.guild.tax.TaxCollectorListMessage import (
    TaxCollectorListMessage,
)
from com.ankamagames.dofus.network.types.game.context.fight.FightResultFighterListEntry import (
    FightResultFighterListEntry,
)
from com.ankamagames.dofus.network.types.game.context.fight.FightResultListEntry import (
    FightResultListEntry,
)
from com.ankamagames.dofus.network.types.game.context.fight.FightResultPlayerListEntry import (
    FightResultPlayerListEntry,
)
from com.ankamagames.dofus.network.types.game.context.fight.FightResultTaxCollectorListEntry import (
    FightResultTaxCollectorListEntry,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightCharacterInformations import (
    GameFightCharacterInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightEntityInformation import (
    GameFightEntityInformation,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterNamedInformations import (
    GameFightFighterNamedInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightMonsterInformations import (
    GameFightMonsterInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightMutantInformations import (
    GameFightMutantInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightResumeSlaveInfo import (
    GameFightResumeSlaveInfo,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightTaxCollectorInformations import (
    GameFightTaxCollectorInformations,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.party.NamedPartyTeam import (
    NamedPartyTeam,
)
from com.ankamagames.dofus.network.types.game.idol.Idol import Idol
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.data.XmlConfig import XmlConfig
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from com.ankamagames.jerakine.sequencer.SerialSequencer import SerialSequencer
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.utils.memory.WeakReference import WeakReference

logger = Logger("Dofus2")


class FightContextFrame(Frame):

    preFightIsActive: bool = True

    currentCell: int = -1

    FIGHT_RESULT_KEY_PREFIX: str = "fightResult_"

    MAX_FIGHT_RESULT: int = 15

    fightResultId: float = 0

    fightResults: dict = dict()

    fightResultIds: list[str] = list[str]()

    INVISIBLE_POSITION_SELECTION: str = "invisible_position"

    GLYPH_GFX_ID: str = "glyphGfxId"

    REACHABLE_CELL_COLOR: int = 26112

    UNREACHABLE_CELL_COLOR: int = 6684672

    _entitiesFrame: FightEntitiesFrame

    _preparationFrame: FightPreparationFrame

    _battleFrame: FightBattleFrame

    _lastEffectEntity: WeakReference

    _timerFighterInfo: BenchmarkTimer = None

    _timerMovementRange: BenchmarkTimer = None

    _currentFighterInfo: GameFightFighterInformations

    _currentMapRenderId: int = -1

    _timelineOverEntity: bool = None

    _timelineOverEntityId: float = None

    _hiddenEntites: list

    _challengesList: list

    _fightType: int

    _fightAttackerId: float

    _namedPartyTeams: list[NamedPartyTeam]

    _fightersPositionsHistory: dict[int, list]

    _fightersRoundStartPosition: dict

    _fightIdols: list[Idol]

    _mustShowTreasureHuntMask: bool = False

    _roleplayGridDisplayed: bool

    isFightLeader: bool

    onlyTheOtherTeamCanPlace: bool = False

    def __init__(self):
        self._hiddenEntites = []
        self._fightersPositionsHistory = dict()
        self._fightersRoundStartPosition = dict()
        super().__init__()
        # TODO: don't forget to init the damage preview later DamagePreview.init()

    def saveResults(self, resultsDescr: object) -> str:
        key: str = self.FIGHT_RESULT_KEY_PREFIX + str(self.fightResultId)
        self.fightResultId += 1
        self.fightResults[key] = resultsDescr
        self.fightResultIds.append(key)
        if len(self.fightResultIds) > self.MAX_FIGHT_RESULT:
            resultsToDeleteKey = self.fightResultIds.pop(0)
            if resultsToDeleteKey is not None and resultsToDeleteKey in self.fightResults:
                del self.fightResults[resultsToDeleteKey]
        return key

    def getResults(self, fightResultKey: str) -> object:
        if fightResultKey in self.fightResults:
            return self.fightResults[fightResultKey]
        return None

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    @property
    def entitiesFrame(self) -> FightEntitiesFrame:
        return self._entitiesFrame

    @property
    def battleFrame(self) -> FightBattleFrame:
        return self._battleFrame

    @property
    def preparationFrame(self) -> FightPreparationFrame:
        return self._preparationFrame

    @property
    def challengesList(self) -> list:
        return self._challengesList

    @property
    def fightType(self) -> int:
        return self._fightType

    @fightType.setter
    def fightType(self, t: int) -> None:
        self._fightType = t
        # TODO: uncomment when party manager is done
        # partyFrame:PartyManagementFrame = Kernel().getWorker().getFrame("PartyManagementFrame")
        # partyFrame.lastFightType = t

    @property
    def isKolossium(self) -> bool:
        return self._fightType == FightTypeEnum.FIGHT_TYPE_PVP_ARENA

    @property
    def timelineOverEntity(self) -> bool:
        return self._timelineOverEntity

    @property
    def timelineOverEntityId(self) -> float:
        return self._timelineOverEntityId

    @property
    def hiddenEntites(self) -> list:
        return self._hiddenEntites

    @property
    def fightersPositionsHistory(self) -> dict:
        return self._fightersPositionsHistory

    def pushed(self) -> bool:
        self.currentCell = -1
        self._entitiesFrame = FightEntitiesFrame()
        self._preparationFrame = FightPreparationFrame(self)
        self._battleFrame = FightBattleFrame()
        self._challengesList = []
        return True

    def getFighterName(self, fighterId: float) -> str:
        fighterInfos = self.getFighterInfos(fighterId)
        if not fighterInfos:
            return "Unknown Fighter"

        if isinstance(fighterInfos, GameFightFighterNamedInformations):
            return fighterInfos.name

        if isinstance(fighterInfos, GameFightMonsterInformations):
            return Monster.getMonsterById(fighterInfos.creatureGenericId).name

        if isinstance(fighterInfos, GameFightEntityInformation):
            compInfos = fighterInfos
            genericName = Companion.getCompanionById(compInfos.entityModelId).name
            if compInfos.masterId != PlayedCharacterManager().id:
                masterName = self.getFighterName(compInfos.masterId)
                name = I18n.getUiText("ui.common.belonging", [genericName, masterName])
            else:
                name = genericName
            return name

        if isinstance(fighterInfos, GameFightTaxCollectorInformations):
            taxInfos = fighterInfos
            return (
                TaxCollectorFirstname.getTaxCollectorFirstnameById(taxInfos.firstNameId).firstname
                + " "
                + TaxCollectorName.getTaxCollectorNameById(taxInfos.lastNameId).name
            )

        else:
            return "Unknown Fighter Type"

    def getFighterLevel(self, fighterId: float) -> int:
        fighterInfos = self.getFighterInfos(fighterId)
        if not fighterInfos:
            return 0
        if isinstance(fighterInfos, GameFightMutantInformations):
            return fighterInfos.powerLevel

        if isinstance(fighterInfos, GameFightCharacterInformations):
            return fighterInfos.level

        if isinstance(fighterInfos, GameFightEntityInformation):
            return fighterInfos.level

        if isinstance(fighterInfos, GameFightMonsterInformations):
            if self.fightType == FightTypeEnum.FIGHT_TYPE_BREACH:
                minLevel = float("inf")
                for entity in self._entitiesFrame.entities.values():
                    if isinstance(
                        entity,
                        GameFightMonsterInformations,
                    ):
                        creatureLevel = entity.creatureLevel
                    if fighterInfos.creatureGenericId == entity.creatureGenericId and entity.stats.summoned:
                        return creatureLevel
                    if not entity.stats.summoned:
                        if minLevel > creatureLevel:
                            minLevel = creatureLevel
                return minLevel
            if fighterInfos.stats.summoned:
                return self.getFighterLevel(fighterInfos.stats.summoner)
            return fighterInfos.creatureLevel
        if isinstance(fighterInfos, GameFightTaxCollectorInformations):
            return fighterInfos.level
        else:
            return 0

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameFightStartingMessage):
            gfsmsg = msg
            fevth.FightEventsHelper().reset()
            self.fightType = gfsmsg.fightType
            self._fightAttackerId = gfsmsg.attackerId
            PlayedCharacterManager().fightId = gfsmsg.fightId
            if PlayerManager().kisServerPort > 0:
                logger.log(
                    2,
                    "KIS fight started : "
                    + str(gfsmsg.fightId)
                    + "-"
                    + str(PlayedCharacterManager().currentMap.mapId)
                    + " (port : "
                    + str(PlayerManager().kisServerPort)
                    + ")",
                )
            else:
                logger.log(
                    2,
                    "Game fight started : "
                    + str(gfsmsg.fightId)
                    + "-"
                    + str(PlayedCharacterManager().currentMap.mapId)
                    + " (port : "
                    + str(PlayerManager().gameServerPort)
                    + ")",
                )
            CurrentPlayedFighterManager().currentFighterId = PlayedCharacterManager().id
            CurrentPlayedFighterManager().getSpellCastManager().currentTurn = 1
            return True

        elif isinstance(msg, CurrentMapMessage):
            mcmsg = msg
            logger.debug(f"[FightContext] Loading the fight map {msg.mapId}...")
            if isinstance(mcmsg, CurrentMapInstanceMessage):
                mdm.MapDisplayManager().mapInstanceId = mcmsg.instantiatedMapId
            else:
                mdm.MapDisplayManager().mapInstanceId = 0
            wp = WorldPointWrapper(mcmsg.mapId)
            EntitiesManager().clearEntities()
            mdm.MapDisplayManager().loadMap(mcmsg.mapId)
            PlayedCharacterManager().currentMap = wp
            PlayedCharacterManager().currentSubArea = SubArea.getSubAreaByMapId(mcmsg.mapId)
            return False

        elif isinstance(msg, MapLoadedMessage):
            gcrmsg = GameContextReadyMessage()
            gcrmsg.init(mdm.MapDisplayManager().currentMapPoint.mapId)
            ConnectionsHandler.getConnection().send(gcrmsg)
            return True

        elif isinstance(msg, GameFightResumeMessage):
            gfrmsg = msg
            playerId = PlayedCharacterManager().id
            CurrentPlayedFighterManager().setCurrentSummonedCreature(gfrmsg.summonCount, playerId)
            CurrentPlayedFighterManager().setCurrentSummonedBomb(gfrmsg.bombCount, playerId)
            self._battleFrame.turnsCount = gfrmsg.gameTurn
            self._fightIdols = gfrmsg.idols
            if isinstance(msg, GameFightResumeWithSlavesMessage):
                gfrwsmsg = msg
                cooldownInfos = gfrwsmsg.slavesInfo
            else:
                cooldownInfos = list[GameFightResumeSlaveInfo]()
            playerCoolDownInfo = GameFightResumeSlaveInfo()
            playerCoolDownInfo.spellCooldowns = gfrmsg.spellCooldowns
            playerCoolDownInfo.slaveId = PlayedCharacterManager().id
            cooldownInfos.insert(0, playerCoolDownInfo)
            playedFighterManager = CurrentPlayedFighterManager()
            for cd in cooldownInfos:
                spellCastManager = playedFighterManager.getSpellCastManagerById(cd.slaveId)
                spellCastManager.currentTurn = gfrmsg.gameTurn
                spellCastManager.updateCooldowns(cd.spellCooldowns)
                if cd.slaveId != playerId:
                    CurrentPlayedFighterManager().setCurrentSummonedCreature(cd.summonCount, cd.slaveId)
                    CurrentPlayedFighterManager().setCurrentSummonedBomb(cd.bombCount, cd.slaveId)
            castingSpellPool = dict()
            for buff in gfrmsg.effects:
                if not castingSpellPool.get(buff.effect.targetId):
                    castingSpellPool[buff.effect.targetId] = {}
                targetPool = castingSpellPool[buff.effect.targetId]
                if not targetPool.get(buff.effect.turnDuration):
                    targetPool[buff.effect.turnDuration] = {}
                durationPool = targetPool[buff.effect.turnDuration]
                castingSpell = durationPool.get(buff.effect.spellId)
                if not castingSpell:
                    castingSpell = CastingSpell()
                    castingSpell.casterId = buff.sourceId
                    castingSpell.spell = spellmod.Spell.getSpellById(buff.effect.spellId)
                    durationPool[buff.effect.spellId] = castingSpell
                buffTmp = BuffManager.makeBuffFromEffect(buff.effect, castingSpell, buff.actionId)
                BuffManager().addBuff(buffTmp)
            Kernel().getWorker().addSingleTreatment(self, self.stopReconnection, [])
            return True

        elif isinstance(msg, GameFightUpdateTeamMessage):
            gfutmsg = msg
            PlayedCharacterManager().teamId = gfutmsg.team.teamId
            return True

        elif isinstance(msg, GameFightSpectateMessage):
            return True

        elif isinstance(msg, GameFightSpectatorJoinMessage):
            return True

        elif isinstance(msg, GameFightJoinMessage):
            gfjmsg = msg
            preFightIsActive = not gfjmsg.isFightStarted
            self.fightType = gfjmsg.fightType
            if not Kernel().getWorker().contains("FightEntitiesFrame"):
                Kernel().getWorker().addFrame(self._entitiesFrame)
            if preFightIsActive:
                if not Kernel().getWorker().contains("FightPreparationFrame"):
                    Kernel().getWorker().addFrame(self._preparationFrame)
                self.onlyTheOtherTeamCanPlace = not gfjmsg.isTeamPhase
            else:
                Kernel().getWorker().removeFrame(self._preparationFrame)
                Kernel().getWorker().addFrame(self._battleFrame)
                self.onlyTheOtherTeamCanPlace = False
            PlayedCharacterManager().isSpectator = False
            PlayedCharacterManager().isFighting = True
            timeBeforeStart = gfjmsg.timeMaxBeforeFightStart * 100
            if timeBeforeStart == 0 and preFightIsActive:
                timeBeforeStart = -1
            return False

        elif isinstance(msg, GameFightStartMessage):
            gfsm = msg
            preFightIsActive = False
            Kernel().getWorker().removeFrame(self._preparationFrame)
            CurrentPlayedFighterManager().getSpellCastManager().resetInitialCooldown()
            Kernel().getWorker().addFrame(self._battleFrame)
            self._fightIdols = gfsm.idols
            return True

        elif isinstance(msg, GameContextDestroyMessage):
            Kernel().getWorker().removeFrame(self)
            return False

        elif isinstance(msg, GameFightLeaveMessage):
            gflmsg = msg
            return False

        # if isinstance(msg, TimelineEntityOverAction):
        #     teoa = msg
        #     self._timelineOverEntity = True
        #     self._timelineOverEntityId = teoa.targetId
        #     fscf = Kernel().getWorker().getFrame("FightSpellCastFrame")
        #     self.overEntity(
        #         teoa.targetId,
        #         teoa.showRange,
        #         teoa.highlightTimelineFighter,
        #         teoa.timelineTarget,
        #     )
        #     return True

        # if isinstance(msg, TimelineEntityOutAction):
        #     tleoutaction = msg
        #     entities = self._entitiesFrame.getEntitiesIdsList()
        #     self._timelineOverEntity = False
        #     self.outEntity(tleoutaction.targetId)
        #     return True

        # if isinstance(msg, TogglePointCellAction):
        #     if Kernel().getWorker().contains("PointCellFrame"):
        #         Kernel().getWorker().removeFrame(PointCellFrame())
        #     else:
        #         Kernel().getWorker().addFrame(PointCellFrame())
        #     return True

        elif isinstance(msg, GameFightEndMessage):
            gfemsg = msg
            hardcoreLoots = None
            CurrentPlayedFighterManager().resetPlayerSpellList()
            fevth.FightEventsHelper().sendAllFightEvent(True)
            PlayedCharacterManager().isFighting = False
            PlayedCharacterManager().fightId = -1
            SpellWrapper.removeAllSpellWrapperBut(PlayedCharacterManager().id, None)
            SpellWrapper.resetAllCoolDown(PlayedCharacterManager().id, None)
            SpellModifiersManager.clear()
            if gfemsg.results is None:
                pass
            else:
                fightEnding = FightEndingMessage()
                fightEnding.init()
                Kernel().getWorker().process(fightEnding)
                results = list[FightResultEntryWrapper](len(gfemsg.results) * [None])
                resultIndex = 0
                winners = list[FightResultEntryWrapper]()
                temp = []
                for resultEntry in gfemsg.results:
                    temp.append(resultEntry)
                isSpectator = True
                for i in range(len(temp)):
                    resultEntry = temp[i]
                    if isinstance(resultEntry, FightResultPlayerListEntry):
                        id = resultEntry.id
                        frew = FightResultEntryWrapper(resultEntry, self._entitiesFrame.getEntityInfos(id))
                        frew.alive = resultEntry.alive
                    if isinstance(resultEntry, FightResultTaxCollectorListEntry):
                        id = resultEntry.id
                        frew = FightResultEntryWrapper(
                            resultEntry,
                            self._entitiesFrame.getEntityInfos(id),
                        )
                        frew.alive = resultEntry.alive
                    if isinstance(resultEntry, FightResultFighterListEntry):
                        id = resultEntry.id
                        frew = FightResultEntryWrapper(
                            resultEntry,
                            self._entitiesFrame.getEntityInfos(id),
                        )
                        frew.alive = resultEntry.alive

                    if isinstance(resultEntry, FightResultListEntry):
                        frew = FightResultEntryWrapper(resultEntry, None, isSpectator)

                    frew.fightInitiator = self._fightAttackerId == id
                    frew.wave = resultEntry.wave
                    if (
                        i + 1 < len(temp)
                        and temp[i + 1]
                        and temp[i + 1].outcome == resultEntry.outcome
                        and temp[i + 1].wave != resultEntry.wave
                    ):
                        frew.isLastOfHisWave = True
                    if resultEntry.outcome == FightOutcomeEnum.RESULT_DEFENDER_GROUP:
                        hardcoreLoots = frew
                    else:
                        if resultEntry.outcome == FightOutcomeEnum.RESULT_VICTORY:
                            winners.append(frew)
                        results[resultIndex] = frew
                        resultIndex += 1
                        if frew.id == CurrentPlayedFighterManager().currentFighterId:
                            isSpectator = False

                if hardcoreLoots:
                    currentWinner = 0
                    for loot in hardcoreLoots.rewards.objects:
                        winners[currentWinner].rewards.objects.append(loot)
                        currentWinner += 1
                        currentWinner %= len(winners)
                    kamas = hardcoreLoots.rewards.kamas
                    kamasPerWinner = math.floor(kamas / len(winners))
                    if kamas % len(winners) != 0:
                        kamasPerWinner += 1
                    for winner in winners:
                        if kamas < kamasPerWinner:
                            winner.rewards.kamas = kamas
                        else:
                            winner.rewards.kamas = kamasPerWinner
                        kamas -= winner.rewards.kamas
                winnersName = ""
                losersName = ""
                for namedTeamWO in gfemsg.namedPartyTeamsOutcomes:
                    if namedTeamWO.team.partyName and namedTeamWO.team.partyName != "":
                        if namedTeamWO.outcome == FightOutcomeEnum.RESULT_VICTORY:
                            winnersName = namedTeamWO.team.partyName
                        elif namedTeamWO.outcome == FightOutcomeEnum.RESULT_LOST:
                            losersName = namedTeamWO.team.partyName
                resultsRecap = {
                    "results": results,
                    "rewardRate": gfemsg.rewardRate,
                    "sizeMalus": gfemsg.lootShareLimitMalus,
                    "duration": gfemsg.duration,
                    "challenges": self.challengesList,
                    "turns": self._battleFrame.turnsCount,
                    "fightType": self._fightType,
                    "winnersName": winnersName,
                    "losersName": losersName,
                    "isSpectator": isSpectator,
                }
                if isinstance(msg, BreachGameFightEndMessage):
                    resultsRecap["budget"] = gfemsg.budget
                idols = [fi.id for fi in self._fightIdols]
                resultsRecap["idols"] = idols
                resultsKey = self.saveResults(resultsRecap)
                if not PlayedCharacterManager().isSpectator:
                    fevth.FightEventsHelper().sendFightEvent(FightEventEnum.FIGHT_END, [resultsKey], 0, -1, True)
                if PlayerManager().kisServerPort > 0:
                    pass
            Kernel().getWorker().removeFrame(self)
            # logger.debug(resultsRecap)
            return False

        elif isinstance(msg, ChallengeTargetsListRequestAction):
            ctlra = msg
            ctlrmsg = ChallengeTargetsListRequestMessage()
            ctlrmsg.init(ctlra.challengeId)
            ConnectionsHandler.getConnection().send(ctlrmsg)
            return True

        elif isinstance(msg, ChallengeTargetsListMessage):
            ctlmsg = msg
            return True

        elif isinstance(msg, ChallengeInfoMessage):
            cimsg = msg
            return True

        elif isinstance(msg, ChallengeTargetUpdateMessage):
            return True

        elif isinstance(msg, ChallengeResultMessage):
            return True

        elif isinstance(msg, ArenaFighterLeaveMessage):
            return True

        elif isinstance(msg, MapObstacleUpdateMessage):
            moumsg = msg
            for mo in moumsg.obstacles:
                DataMapProvider().updateCellMovLov(mo.obstacleCellId, mo.state == MapObstacleStateEnum.OBSTACLE_OPENED)
            return True

        elif isinstance(msg, GameActionFightNoSpellCastMessage):
            # logger.debug(f"failed to cast spell {msg.to_json()}")
            return False

        # if isinstance(msg, BreachEnterMessage):
        #     bemsg = msg
        #     PlayedCharacterManager().isInBreach = True
        #     if not Kernel().getWorker().getFrame("BreachFrame"):
        #         breachFrame = BreachFrame()
        #         breachFrame.ownerId = bemsg.owner
        #         Kernel().getWorker().addFrame(breachFrame)
        #     return True

        # if isinstance(msg, BreachExitResponseMessage):
        #     if PlayedCharacterManager().isInBreach:
        #         PlayedCharacterManager().isInBreach = False
        #         if Kernel().getWorker().getFrame("BreachFrame"):
        #             Kernel().getWorker().removeFrame(
        #                 Kernel().getWorker().getFrame("BreachFrame")
        #             )
        #     return True

        elif isinstance(msg, UpdateSpellModifierAction):
            usma = msg
            spellWrapper = SpellWrapper.getSpellWrapperById(usma.spellId, usma.entityId)
            if spellWrapper is not None:
                spellWrapper.versionNum += 1
                if usma.statId == CharacterSpellModificationTypeEnum.CAST_INTERVAL:
                    spellManager = (
                        CurrentPlayedFighterManager()
                        .getSpellCastManagerById(usma.entityId)
                        .getSpellManagerBySpellId(usma.spellId)
                    )
                    if spellManager is not None:
                        spellWrapper.actualCooldown = spellManager.cooldown
                elif usma.statId == CharacterSpellModificationTypeEnum.AP_COST:
                    pass
            return True

        elif isinstance(msg, ArenaFighterIdleMessage):
            return True

        return False

    def pulled(self) -> bool:
        if self._battleFrame:
            Kernel().getWorker().removeFrame(self._battleFrame)
        if self._entitiesFrame:
            Kernel().getWorker().removeFrame(self._entitiesFrame)
        if self._preparationFrame:
            Kernel().getWorker().removeFrame(self._preparationFrame)
        self._lastEffectEntity = None
        if self._timerFighterInfo:
            self._timerFighterInfo.cancel()
        if self._timerMovementRange:
            self._timerMovementRange.cancel()
        self._currentFighterInfo = None
        simf: "SpellInventoryManagementFrame" = Kernel().getWorker().getFrame("SpellInventoryManagementFrame")
        if simf:
            simf.deleteSpellsGlobalCoolDownsData()
        PlayedCharacterManager().isSpectator = False
        return True

    def addToHiddenEntities(self, entityId: float) -> None:
        if entityId not in self._hiddenEntites:
            self._hiddenEntites.append(entityId)

    def removeFromHiddenEntities(self, entityId: float) -> None:
        if entityId in self._hiddenEntites:
            self._hiddenEntites.remove(entityId)

    def initFighterPositionHistory(self, pFighterId: float) -> None:
        if not self._fightersPositionsHistory.get(pFighterId):
            fightContextFrame: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
            self._fightersPositionsHistory[pFighterId] = [
                {
                    "cellId": fightContextFrame.entitiesFrame.getEntityInfos(pFighterId).disposition.cellId,
                    "lives": 2,
                }
            ]

    def getFighterPreviousPosition(self, pFighterId: float) -> int:
        self.initFighterPositionHistory(pFighterId)
        positions: list = self._fightersPositionsHistory[pFighterId]
        savedPos: object = positions[len(positions) - 2] if len(positions) > 1 else None
        return int(savedPos["cellId"] if savedPos else -1)

    def deleteFighterPreviousPosition(self, pFighterId: float) -> None:
        if self._fightersPositionsHistory[pFighterId]:
            self._fightersPositionsHistory[pFighterId].pop()

    def saveFighterPosition(self, pFighterId: float, pCellId: int) -> None:
        self.initFighterPositionHistory(pFighterId)
        self._fightersPositionsHistory[pFighterId].append({"cellId": pCellId, "lives": 2})

    def getFighterRoundStartPosition(self, pFighterId: float) -> int:
        return self._fightersRoundStartPosition[pFighterId]

    def setFighterRoundStartPosition(self, pFighterId: float, cellId: int) -> int:
        self._fightersRoundStartPosition[pFighterId] = cellId
        return cellId

    def refreshTimelineOverEntityInfos(self) -> None:
        if self._timelineOverEntity and self._timelineOverEntityId:
            entity = DofusEntities.getEntity(self._timelineOverEntityId)
            if entity and entity.position:
                FightContextFrame.currentCell = entity.position.cellId

    def getFighterInfos(self, fighterId: float) -> GameFightFighterInformations:
        return self.entitiesFrame.getEntityInfos(fighterId)

    def stopReconnection(self, *args) -> None:
        Kernel().beingInReconection = False

    def sendFightEvents(self) -> None:
        fevth.FightEventsHelper().sendAllFightEvent()