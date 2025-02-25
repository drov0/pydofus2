from types import FunctionType
from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.berilia.managers.KernelEvent import KernelEvent
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
    KernelEventsManager
from pydofus2.com.ankamagames.dofus.enums.ElementEnum import ElementEnum
from pydofus2.com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import \
    SpellWrapper
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.ISpellCastProvider import \
    ISpellCastProvider
from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.MarkedCellsManager import \
    MarkedCellsManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.messages.GameActionFightLeaveMessage import \
    GameActionFightLeaveMessage
from pydofus2.com.ankamagames.dofus.logic.game.fight.miscs.ActionIdHelper import \
    ActionIdHelper
from pydofus2.com.ankamagames.dofus.logic.game.fight.miscs.ActionIdProtocol import \
    ActionIdProtocol
from pydofus2.com.ankamagames.dofus.logic.game.fight.miscs.FightEntitiesHolder import \
    FightEntitiesHolder
from pydofus2.com.ankamagames.dofus.logic.game.fight.miscs.SpellScriptBuffer import \
    SpellScriptBuffer
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightActionPointsLossDodgeStep import \
    FightActionPointsLossDodgeStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightActionPointsVariationStep import \
    FightActionPointsVariationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightCarryCharacterStep import \
    FightCarryCharacterStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightChangeVisibilityStep import \
    FightChangeVisibilityStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightCloseCombatStep import \
    FightCloseCombatStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightDeathStep import \
    FightDeathStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightDispellEffectStep import \
    FightDispellEffectStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightDispellSpellStep import \
    FightDispellSpellStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightDispellStep import \
    FightDispellStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightDisplayBuffStep import \
    FightDisplayBuffStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightEnteringStateStep import \
    FightEnteringStateStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightEntityMovementStep import \
    FightEntityMovementStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightEntitySlideStep import \
    FightEntitySlideStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightExchangePositionsStep import \
    FightExchangePositionsStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightFighterStatsListStep import \
    FightFighterStatsListStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightInvisibleTemporarilyDetectedStep import \
    FightInvisibleTemporarilyDetectedStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightKillStep import \
    FightKillStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightLeavingStateStep import \
    FightLeavingStateStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightLifeVariationStep import \
    FightLifeVariationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightMarkActivateStep import \
    FightMarkActivateStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightMarkCellsStep import \
    FightMarkCellsStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightMarkTriggeredStep import \
    FightMarkTriggeredStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightModifyEffectsDurationStep import \
    FightModifyEffectsDurationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightMovementPointsLossDodgeStep import \
    FightMovementPointsLossDodgeStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightMovementPointsVariationStep import \
    FightMovementPointsVariationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightPlaySpellScriptStep import \
    FightPlaySpellScriptStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightReducedDamagesStep import \
    FightReducedDamagesStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightReflectedDamagesStep import \
    FightReflectedDamagesStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightReflectedSpellStep import \
    FightReflectedSpellStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightRefreshFighterStep import \
    FightRefreshFighterStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightShieldPointsVariationStep import \
    FightShieldPointsVariationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightSpellCastStep import \
    FightSpellCastStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightSpellCooldownVariationStep import \
    FightSpellCooldownVariationStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightSpellImmunityStep import \
    FightSpellImmunityStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightStealingKamasStep import \
    FightStealingKamasStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightSummonStep import \
    FightSummonStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightTackledStep import \
    FightTackledStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightTeleportStep import \
    FightTeleportStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightTemporaryBoostStep import \
    FightTemporaryBoostStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightThrowCharacterStep import \
    FightThrowCharacterStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightTurnListStep import \
    FightTurnListStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightUnmarkCellsStep import \
    FightUnmarkCellsStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightUpdateStatStep import \
    FightUpdateStatStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightVanishStep import \
    FightVanishStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.FightVisibilityStep import \
    FightVisibilityStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import \
    IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.MarkInstance import \
    MarkInstance
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.StatBuff import \
    StatBuff
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.StateBuff import \
    StateBuff
from pydofus2.com.ankamagames.dofus.network.enums.GameActionFightInvisibilityStateEnum import \
    GameActionFightInvisibilityStateEnum
from pydofus2.com.ankamagames.dofus.network.enums.GameActionMarkTypeEnum import \
    GameActionMarkTypeEnum

from pydofus2.com.ankamagames.jerakine.entities.interfaces.IMovable import \
    IMovable
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.ParallelStartSequenceStep import \
    ParallelStartSequenceStep
from pydofus2.com.ankamagames.jerakine.types.events.SequencerEvent import \
    SequencerEvent
from pydofus2.com.ankamagames.jerakine.utils.display.spellZone.SpellShapeEnum import \
    SpellShapeEnum

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import (
        FightBattleFrame,
    )

from pydofus2.com.ankamagames.dofus.datacenter.effects.Effect import Effect
from pydofus2.com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceDice import \
    EffectInstanceDice
from pydofus2.com.ankamagames.dofus.datacenter.monsters.Monster import Monster
from pydofus2.com.ankamagames.dofus.datacenter.spells.Spell import Spell
from pydofus2.com.ankamagames.dofus.enums.ActionIds import ActionIds
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.MapMovementAdapter import \
    MapMovementAdapter
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import \
    DofusEntities
from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.BuffManager import \
    BuffManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import \
    CurrentPlayedFighterManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.BasicBuff import \
    BasicBuff
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.CastingSpell import \
    CastingSpell
from pydofus2.com.ankamagames.dofus.misc.utils.GameDebugManager import \
    GameDebugManager
from pydofus2.com.ankamagames.dofus.network.enums.FightSpellCastCriticalEnum import \
    FightSpellCastCriticalEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import \
    AbstractGameActionMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightActivateGlyphTrapMessage import \
    GameActionFightActivateGlyphTrapMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCarryCharacterMessage import \
    GameActionFightCarryCharacterMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightChangeLookMessage import \
    GameActionFightChangeLookMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCloseCombatMessage import \
    GameActionFightCloseCombatMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDeathMessage import \
    GameActionFightDeathMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDispellableEffectMessage import \
    GameActionFightDispellableEffectMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDispellEffectMessage import \
    GameActionFightDispellEffectMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDispellMessage import \
    GameActionFightDispellMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDispellSpellMessage import \
    GameActionFightDispellSpellMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDodgePointLossMessage import \
    GameActionFightDodgePointLossMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightDropCharacterMessage import \
    GameActionFightDropCharacterMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightExchangePositionsMessage import \
    GameActionFightExchangePositionsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightInvisibilityMessage import \
    GameActionFightInvisibilityMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightInvisibleDetectedMessage import \
    GameActionFightInvisibleDetectedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightKillMessage import \
    GameActionFightKillMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightLifeAndShieldPointsLostMessage import \
    GameActionFightLifeAndShieldPointsLostMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightLifePointsGainMessage import \
    GameActionFightLifePointsGainMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightLifePointsLostMessage import \
    GameActionFightLifePointsLostMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightMarkCellsMessage import \
    GameActionFightMarkCellsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightModifyEffectsDurationMessage import \
    GameActionFightModifyEffectsDurationMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightMultipleSummonMessage import \
    GameActionFightMultipleSummonMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightPointsVariationMessage import \
    GameActionFightPointsVariationMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightReduceDamagesMessage import \
    GameActionFightReduceDamagesMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightReflectDamagesMessage import \
    GameActionFightReflectDamagesMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightReflectSpellMessage import \
    GameActionFightReflectSpellMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSlideMessage import \
    GameActionFightSlideMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSpellCastMessage import \
    GameActionFightSpellCastMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSpellCooldownVariationMessage import \
    GameActionFightSpellCooldownVariationMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSpellImmunityMessage import \
    GameActionFightSpellImmunityMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightStealKamaMessage import \
    GameActionFightStealKamaMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSummonMessage import \
    GameActionFightSummonMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightTackledMessage import \
    GameActionFightTackledMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightTeleportOnSameMapMessage import \
    GameActionFightTeleportOnSameMapMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightThrowCharacterMessage import \
    GameActionFightThrowCharacterMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightTriggerEffectMessage import \
    GameActionFightTriggerEffectMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightTriggerGlyphTrapMessage import \
    GameActionFightTriggerGlyphTrapMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightUnmarkCellsMessage import \
    GameActionFightUnmarkCellsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightVanishMessage import \
    GameActionFightVanishMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceEndMessage import \
    SequenceEndMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceStartMessage import \
    SequenceStartMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.stats.FighterStatsListMessage import \
    FighterStatsListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.fight.character.GameFightRefreshFighterMessage import \
    GameFightRefreshFighterMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.fight.character.GameFightShowFighterMessage import \
    GameFightShowFighterMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.fight.character.GameFightShowFighterRandomStaticPoseMessage import \
    GameFightShowFighterRandomStaticPoseMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnListMessage import \
    GameFightTurnListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.fight.RefreshCharacterStatsMessage import \
    RefreshCharacterStatsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameMapMovementMessage import \
    GameMapMovementMessage
from pydofus2.com.ankamagames.dofus.network.types.game.actions.fight.AbstractFightDispellableEffect import \
    AbstractFightDispellableEffect
from pydofus2.com.ankamagames.dofus.network.types.game.actions.fight.FightTemporaryBoostEffect import \
    FightTemporaryBoostEffect
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightCharacterInformations import \
    GameFightCharacterInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightEntityInformation import \
    GameFightEntityInformation
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import \
    GameFightFighterInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterNamedInformations import \
    GameFightFighterNamedInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightMonsterInformations import \
    GameFightMonsterInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightSpellCooldown import \
    GameFightSpellCooldown
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.SpawnCharacterInformation import \
    SpawnCharacterInformation
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.SpawnCompanionInformation import \
    SpawnCompanionInformation
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.SpawnMonsterInformation import \
    SpawnMonsterInformation
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.SpawnScaledMonsterInformation import \
    SpawnScaledMonsterInformation
from pydofus2.com.ankamagames.dofus.network.types.game.context.GameContextActorInformations import \
    GameContextActorInformations
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import \
    AbstractSequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencable import \
    ISequencable
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from pydofus2.com.ankamagames.jerakine.sequencer.SerialSequencer import \
    SerialSequencer
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from pydofus2.com.ankamagames.jerakine.types.positions.MovementPath import \
    MovementPath


class FightSequenceFrame(Frame, ISpellCastProvider):
    FIGHT_SEQUENCERS_CATEGORY: str = "FightSequencer"

    _lastCastingSpell: CastingSpell

    _currentInstanceId: int = 0

    _castingSpell: CastingSpell

    _castingSpells: list[CastingSpell]

    _stepsBuffer: list[ISequencable]

    _sequenceEndCallback: FunctionType

    _subSequenceWaitingCount: int

    _sequencer: SerialSequencer

    _parent: "FightSequenceFrame"

    _fightBattleFrame: "FightBattleFrame"

    _instanceId: int

    _teleportThroughPortal: bool

    _playSpellScriptStep: FightPlaySpellScriptStep

    _spellScriptTemporaryBuffer: SpellScriptBuffer

    def __init__(self, pFightBattleFrame: "FightBattleFrame", parent: "FightSequenceFrame" = None):
        super().__init__()
        self._instanceId = FightSequenceFrame._currentInstanceId
        FightSequenceFrame._currentInstanceId = (1 + FightSequenceFrame._currentInstanceId) % 4000
        self._fightEntitiesFrame = None
        self._fightBattleFrame = pFightBattleFrame
        self._parent = parent
        self._sequencer = None
        self._stepsBuffer: list = []
        self._castingSpell = None
        self._castingSpells = list[CastingSpell]()
        self._sequenceEndCallback = None
        self._teleportThroughPortal = False
        self._subSequenceWaitingCount = 0
        self._activeSubSequenceCount = 0
        self.ackIdent: int = None
        self.mustAck: bool = None

    @property
    def lastCastingSpell(self) -> CastingSpell:
        return self._lastCastingSpell

    @property
    def currentInstanceId(self) -> int:
        return FightSequenceFrame._currentInstanceId

    @property
    def priority(self) -> int:
        return Priority.HIGHEST

    @property
    def castingSpell(self) -> CastingSpell:
        if self._castingSpells and len(self._castingSpells) > 1:
            return self._castingSpells[-1]
        return self._castingSpell

    @property
    def stepsBuffer(self) -> list[ISequencable]:
        return self._stepsBuffer

    @property
    def parent(self) -> "FightSequenceFrame":
        return self._parent

    @property
    def isWaiting(self) -> bool:
        return self._subSequenceWaitingCount != 0

    @property
    def instanceId(self) -> int:
        return self._instanceId

    def pushed(self) -> bool:
        return True

    def pulled(self) -> bool:
        FightSequenceFrame._currentInstanceId = 0
        self._stepsBuffer = None
        self._castingSpell = None
        self._castingSpells = None
        self._lastCastingSpell = None
        self._sequenceEndCallback = None
        self._parent = None
        self._fightBattleFrame = None
        self._fightEntitiesFrame = None
        self._sequencer.clear()
        return True

    def addSubSequence(self, sequence: ISequencer) -> None:
        self._subSequenceWaitingCount += 1
        # Logger().debug(f"Adding ParallelStartSequenceStep to sequence #{self._instanceId}")
        self._stepsBuffer.append(ParallelStartSequenceStep([sequence], False))

    def process(self, msg: Message) -> bool:
        closeCombatWeaponId = 0
        if isinstance(msg, GameFightRefreshFighterMessage):
            gfrfmsg = msg
            self._stepsBuffer.append(FightRefreshFighterStep(gfrfmsg.informations))
            return True

        if isinstance(msg, (GameActionFightCloseCombatMessage, GameActionFightSpellCastMessage)):
            forceDetailedLogs = GameDebugManager().detailedFightLog_showEverything
            if not self._castingSpells:
                self._castingSpells = list[CastingSpell]()

            if isinstance(msg, GameActionFightSpellCastMessage):
                gafscmsg = msg
                if forceDetailedLogs:
                    gafscmsg.verboseCast = True

            else:
                gafccmsg = msg
                closeCombatWeaponId = gafccmsg.weaponGenericId
                gafscmsg = GameActionFightSpellCastMessage()
                gafscmsg.init(
                    gafccmsg.targetId,
                    gafccmsg.destinationCellId,
                    gafccmsg.critical,
                    gafccmsg.silentCast,
                    gafccmsg.verboseCast,
                    gafccmsg.actionId,
                    gafccmsg.sourceId,
                )
                if forceDetailedLogs:
                    gafscmsg.verboseCast = True
            fightEntitiesFrame = Kernel().fightEntitiesFrame
            sourceCellId = -1
            if fightEntitiesFrame and fightEntitiesFrame.hasEntity(gafscmsg.sourceId):
                fighterInfo = fightEntitiesFrame.getEntityInfos(gafscmsg.sourceId)
                if fighterInfo:
                    sourceCellId = fighterInfo.disposition.cellId
            tempCastingSpell = CastingSpell()
            tempCastingSpell.casterId = gafscmsg.sourceId
            tempCastingSpell.spell = Spell.getSpellById(gafscmsg.spellId)
            tempCastingSpell.spellRank = tempCastingSpell.spell.getSpellLevel(gafscmsg.spellLevel)
            tempCastingSpell.isCriticalFail = gafscmsg.critical == FightSpellCastCriticalEnum.CRITICAL_FAIL
            tempCastingSpell.isCriticalHit = gafscmsg.critical == FightSpellCastCriticalEnum.CRITICAL_HIT
            tempCastingSpell.silentCast = gafscmsg.silentCast
            tempCastingSpell.portalIds = gafscmsg.portalsIds
            tempCastingSpell.portalMapPoints = MarkedCellsManager().getMapPointsFromMarkIds(gafscmsg.portalsIds)
            if GameDebugManager().buffsDebugActivated:
                Logger().debug(
                    "\r[BUFFS DEBUG] Sort "
                    + tempCastingSpell.spell.name
                    + " ("
                    + str(gafscmsg.spellId)
                    + ") casted by "
                    + str(gafscmsg.sourceId)
                    + " on "
                    + str(gafscmsg.targetId)
                    + " (cell "
                    + str(gafscmsg.destinationCellId)
                    + ")"
                )
            if not CurrentPlayedFighterManager().currentFighterId:
                BuffManager().spellBuffsToIgnore.append(tempCastingSpell)
            if gafscmsg.destinationCellId != -1:
                tempCastingSpell.targetedCell = MapPoint.fromCellId(gafscmsg.destinationCellId)
            if gafscmsg and gafscmsg.actionId == ActionIds.ACTION_FINISH_MOVE:
                return True
            if self._castingSpell:
                if closeCombatWeaponId != 0:
                    self.pushStep(
                        FightCloseCombatStep(
                            gafscmsg.sourceId,
                            closeCombatWeaponId,
                            gafscmsg.critical,
                            gafscmsg.verboseCast,
                        )
                    )
                elif sourceCellId >= 0:
                    self.pushStep(
                        FightSpellCastStep(
                            gafscmsg.sourceId,
                            gafscmsg.destinationCellId,
                            sourceCellId,
                            gafscmsg.spellId,
                            gafscmsg.spellLevel,
                            gafscmsg.critical,
                            gafscmsg.verboseCast,
                        )
                    )
                self._castingSpells.append(tempCastingSpell)
                if isinstance(msg, GameActionFightCloseCombatMessage):
                    self._castingSpell.weaponId = msg.weaponGenericId
                    self.pushPlaySpellScriptStep(
                        7,
                        gafscmsg.sourceId,
                        gafscmsg.destinationCellId,
                        gafscmsg.spellId,
                        gafscmsg.spellLevel,
                    )
                elif not tempCastingSpell.isCriticalFail:
                    fxScriptId = tempCastingSpell.spell.getScriptId(tempCastingSpell.isCriticalHit)
                    self.pushPlaySpellScriptStep(
                        fxScriptId,
                        gafscmsg.sourceId,
                        gafscmsg.destinationCellId,
                        gafscmsg.spellId,
                        gafscmsg.spellLevel,
                    )
                return True
            self._castingSpell = tempCastingSpell
            self._spellScriptTemporaryBuffer = SpellScriptBuffer(self._castingSpell)
            if isinstance(msg, GameActionFightCloseCombatMessage):
                self._castingSpell.weaponId = GameActionFightCloseCombatMessage(msg).weaponGenericId
                self._playSpellScriptStep = self.pushPlaySpellScriptStep(
                    7,
                    gafscmsg.sourceId,
                    gafscmsg.destinationCellId,
                    gafscmsg.spellId,
                    gafscmsg.spellLevel,
                    self._spellScriptTemporaryBuffer,
                )
            elif not self._castingSpell.isCriticalFail:
                fxScriptId = self._castingSpell.spell.getScriptId(self._castingSpell.isCriticalHit)
                self._playSpellScriptStep = self.pushPlaySpellScriptStep(
                    fxScriptId,
                    gafscmsg.sourceId,
                    gafscmsg.destinationCellId,
                    gafscmsg.spellId,
                    gafscmsg.spellLevel,
                    self._spellScriptTemporaryBuffer,
                )
            self._stepsBuffer.extend(self._spellScriptTemporaryBuffer.stepsBuffer)
            if gafscmsg.critical != FightSpellCastCriticalEnum.CRITICAL_FAIL:
                spellTargetEntities = []
                spellTargetEntities.append(gafscmsg.targetId)
                CurrentPlayedFighterManager().getSpellCastManagerById(gafscmsg.sourceId).castSpell(
                    gafscmsg.spellId, gafscmsg.spellLevel, spellTargetEntities
                )
            gafscmsg.critical == FightSpellCastCriticalEnum.CRITICAL_HIT
            entities = Kernel().fightEntitiesFrame.entities
            fighter = entities[gafscmsg.sourceId]
            if closeCombatWeaponId != 0:
                self.pushStep(
                    FightCloseCombatStep(
                        gafscmsg.sourceId,
                        closeCombatWeaponId,
                        gafscmsg.critical,
                        gafscmsg.verboseCast,
                    )
                )
            else:
                self.pushStep(
                    FightSpellCastStep(
                        gafscmsg.sourceId,
                        gafscmsg.destinationCellId,
                        sourceCellId,
                        gafscmsg.spellId,
                        gafscmsg.spellLevel,
                        gafscmsg.critical,
                        gafscmsg.verboseCast,
                    )
                )
            playerManager = PlayedCharacterManager()
            isAlly = False
            if (
                entities
                and entities.get(playerManager.id)
                and fighter
                and entities[playerManager.id].spawnInfo.teamId == fighter.spawnInfo.teamId
            ):
                isAlly = True
            if isAlly and not self._castingSpell.isCriticalFail:
                isSpellKnown = False
                for spellKnown in playerManager.spellsInventory:
                    if spellKnown.id == gafscmsg.spellId:
                        isSpellKnown = True
                        playerSpellLevel = spellKnown.spellLevelInfos
                spell = Spell.getSpellById(gafscmsg.spellId)
                castSpellLevel = spell.getSpellLevel(gafscmsg.spellLevel)
                if castSpellLevel.globalCooldown:
                    if isSpellKnown and gafscmsg.sourceId != playerManager.id:
                        if castSpellLevel.globalCooldown == -1:
                            gcdValue = playerSpellLevel.minCastInterval
                        else:
                            gcdValue = castSpellLevel.globalCooldown
                        spellCastManager = CurrentPlayedFighterManager().getSpellCastManagerById(playerManager.id)
                        if spellCastManager:
                            spellManager = spellCastManager.getSpellManagerBySpellId(
                                gafscmsg.spellId, True, castSpellLevel.id
                            )
                            if spellCastManager.currentTurn > 1:
                                if spellManager and spellManager.cooldown <= gcdValue:
                                    self.pushStep(
                                        FightSpellCooldownVariationStep(
                                            playerManager.id,
                                            0,
                                            gafscmsg.spellId,
                                            gcdValue,
                                            True,
                                        )
                                    )
                            else:
                                self.pushStep(
                                    FightSpellCooldownVariationStep(
                                        playerManager.id,
                                        0,
                                        gafscmsg.spellId,
                                        gcdValue,
                                        True,
                                    )
                                )
                    simf = Kernel().spellInventoryManagementFrame
                    for fighterInfos in entities:
                        gfsc = GameFightSpellCooldown()
                        if (
                            isinstance(fighterInfos, GameFightEntityInformation)
                            and gafscmsg.sourceId != fighterInfos.contextualId
                        ):
                            gfsc.init(gafscmsg.spellId, castSpellLevel.globalCooldown)
                            simf.addSpellGlobalCoolDownInfo(fighterInfos.contextualId, gfsc)
                        elif (
                            isinstance(fighterInfos, GameFightCharacterInformations)
                            and gafscmsg.sourceId != fighterInfos.contextualId
                            and fighterInfos.contextualId == playerManager.id
                        ):
                            gfsc.init(gafscmsg.spellId, castSpellLevel.globalCooldown)
                            simf.addSpellGlobalCoolDownInfo(fighterInfos.contextualId, gfsc)
            if not fightEntitiesFrame:
                return True
            target = fightEntitiesFrame.getEntityInfos(gafscmsg.targetId)
            if target and target.disposition.cellId == -1:
                for ei in self._castingSpell.spellRank.effects:
                    if hasattr(ei, "zoneShape"):
                        shape = ei.zoneShape
                        break
                if shape == SpellShapeEnum.P:
                    ts = DofusEntities().getEntity(gafscmsg.targetId)
                    if ts and self._castingSpell and self._castingSpell.targetedCell:
                        targetedCell = InteractiveCellManager().getCell(self._castingSpell.targetedCell.cellId)
                        cellPos = targetedCell.parent.localToGlobal(
                            Point(
                                targetedCell.x + targetedCell.width / 2,
                                targetedCell.y + targetedCell.height / 2,
                            )
                        )
                        ts.x = cellPos.x
                        ts.y = cellPos.y
            self._castingSpells.append(self._castingSpell)
            KernelEventsManager().send(
                KernelEvent.FighterCastedSpell,
                gafscmsg.sourceId,
                gafscmsg.destinationCellId,
                sourceCellId,
                gafscmsg.spellId,
            )
            return True

        if isinstance(msg, GameMapMovementMessage):
            self.fighterHasMoved(msg)
            return False

        if isinstance(msg, FighterStatsListMessage):
            fslmsg = msg
            self.pushStep(FightFighterStatsListStep(fslmsg.stats))
            return True

        if isinstance(msg, GameActionFightPointsVariationMessage):
            gafpvmsg = msg
            self.pushPointsVariationStep(gafpvmsg.targetId, gafpvmsg.actionId, gafpvmsg.delta)
            return True

        if isinstance(msg, GameActionFightLifeAndShieldPointsLostMessage):
            gaflasplmsg = msg
            self.pushStep(
                FightShieldPointsVariationStep(gaflasplmsg.targetId, -gaflasplmsg.shieldLoss, gaflasplmsg.elementId)
            )
            self.pushStep(
                FightLifeVariationStep(
                    gaflasplmsg.targetId,
                    -gaflasplmsg.loss,
                    -gaflasplmsg.permanentDamages,
                    gaflasplmsg.elementId,
                )
            )
            return True

        if isinstance(msg, GameActionFightLifePointsGainMessage):
            gaflpgmsg = msg
            self.pushStep(FightLifeVariationStep(gaflpgmsg.targetId, gaflpgmsg.delta, 0, ElementEnum.ELEMENT_NONE))
            return True

        if isinstance(msg, GameActionFightLifePointsLostMessage):
            gaflplmsg = msg
            self.pushStep(
                FightLifeVariationStep(
                    gaflplmsg.targetId,
                    -gaflplmsg.loss,
                    -gaflplmsg.permanentDamages,
                    gaflplmsg.elementId,
                )
            )
            return True

        if isinstance(msg, GameActionFightTeleportOnSameMapMessage):
            gaftosmmsg = msg
            self.fighterHasBeenTeleported(gaftosmmsg)
            return True

        if isinstance(msg, GameActionFightExchangePositionsMessage):
            self.fightersExchangedPositions(msg)
            return True

        if isinstance(msg, GameActionFightSlideMessage):
            fightContextFrame_gafsmsg = Kernel().fightContextFrame
            slideTargetInfos = fightContextFrame_gafsmsg.entitiesFrame.getEntityInfos(msg.targetId)
            if slideTargetInfos:
                fightContextFrame_gafsmsg.saveFighterPosition(msg.targetId, msg.endCellId)
                self.pushSlideStep(msg.targetId, msg.startCellId, msg.endCellId)
            return True

        if isinstance(msg, GameActionFightSummonMessage):
            gafsnmsg = msg
            self.fighterSummonEntity(gafsnmsg)
            return True

        if isinstance(msg, GameActionFightMultipleSummonMessage):
            gafmsmsg = msg
            gffinfos = GameFightFighterInformations()
            self.pushStep(
                FightUpdateStatStep(
                    0,
                    [],
                )
            )
            gffinfos = self.fighterSummonMultipleEntities(gafmsmsg, gffinfos)
            return True

        if isinstance(msg, RefreshCharacterStatsMessage):
            rcmsg = msg
            if Kernel().fightEntitiesFrame:
                infos = Kernel().fightEntitiesFrame.getEntityInfos(rcmsg.fighterId)
                if infos:
                    infos.stats = rcmsg.stats
            self.pushStep(FightUpdateStatStep(rcmsg.fighterId, rcmsg.stats.characteristics.characteristics))
            return True

        if isinstance(msg, GameActionFightMarkCellsMessage):
            self.cellsHasBeenMarked(msg)
            return True

        if isinstance(msg, GameActionFightUnmarkCellsMessage):
            self.pushStep(FightUnmarkCellsStep(msg.markId))
            return True

        if isinstance(msg, GameActionFightChangeLookMessage):
            entity = Kernel().fightEntitiesFrame.getEntityInfos(msg.targetId)
            Logger().debug(f"Fighter {msg.targetId} changed look from {entity.look.bonesId} to {msg.entityLook.bonesId}")
            entity.look = msg.entityLook
            return True

        if isinstance(msg, GameActionFightInvisibilityMessage):
            inviInfo = Kernel().fightEntitiesFrame.getEntityInfos(msg.targetId)
            if not inviInfo:
                return True
            stateName = GameActionFightInvisibilityStateEnum.getStateName(msg.state)
            Logger().info(
                f"[BUFFS] Invisibility change of ({msg.targetId}) cell ({inviInfo.disposition.cellId}) new state ({stateName})"
            )
            Kernel().fightEntitiesFrame.setLastKnownEntityPosition(msg.targetId, inviInfo.disposition.cellId)
            Kernel().fightEntitiesFrame.setLastKnownEntityMovementPoint(msg.targetId, 0, True)
            self.pushStep(FightChangeVisibilityStep(msg.targetId, msg.state))
            return True

        if isinstance(msg, GameActionFightLeaveMessage):
            gaflmsg = msg
            self.fighterHasLeftBattle(gaflmsg)
            return True

        if isinstance(msg, GameActionFightDeathMessage):
            gafdmsg = msg
            fightEntitiesFrame = Kernel().fightEntitiesFrame
            self.fighterHasBeenKilled(gafdmsg)
            return True

        if isinstance(msg, GameActionFightVanishMessage):
            gafvmsg = msg
            self.pushStep(FightVanishStep(gafvmsg.targetId, gafvmsg.sourceId))
            entityInfosv = Kernel().fightEntitiesFrame.getEntityInfos(gafvmsg.targetId)
            if isinstance(entityInfosv, GameFightFighterInformations):
                entityInfosv.spawnInfo.alive = False
            return True

        if isinstance(msg, GameActionFightTriggerEffectMessage):
            return True

        if isinstance(msg, GameActionFightDispellEffectMessage):
            gafdiemsg = msg
            if GameDebugManager().buffsDebugActivated:
                Logger().debug(
                    "[BUFFS DEBUG] Message of the retrieval of buff "
                    + str(gafdiemsg.boostUID)
                    + " belonging to "
                    + str(gafdiemsg.targetId)
                )
            self.pushStep(FightDispellEffectStep(gafdiemsg.targetId, gafdiemsg.boostUID))
            return True

        if isinstance(msg, GameActionFightDispellSpellMessage):
            gafdsmsg = msg
            if GameDebugManager().buffsDebugActivated:
                Logger().debug(
                    "[BUFFS DEBUG] Message de retrait des buffs du sort "
                    + str(gafdsmsg.spellId)
                    + " de "
                    + str(gafdsmsg.targetId)
                )
            self.pushStep(FightDispellSpellStep(gafdsmsg.targetId, gafdsmsg.spellId, gafdsmsg.verboseCast))
            return True

        if isinstance(msg, GameActionFightDispellMessage):
            gafdimsg = msg
            if GameDebugManager().buffsDebugActivated:
                Logger().debug("[BUFFS DEBUG] Message de retrait de tous les buffs de " + str(gafdimsg.targetId))
            self.pushStep(FightDispellStep(gafdimsg.targetId))
            return True

        if isinstance(msg, GameActionFightDodgePointLossMessage):
            gafdplmsg = msg
            self.pushPointsLossDodgeStep(gafdplmsg.targetId, gafdplmsg.actionId, gafdplmsg.amount)
            return True

        if isinstance(msg, GameActionFightSpellCooldownVariationMessage):
            gafscvmsg = msg
            self.pushStep(
                FightSpellCooldownVariationStep(
                    gafscvmsg.targetId,
                    gafscvmsg.actionId,
                    gafscvmsg.spellId,
                    gafscvmsg.value,
                )
            )
            return True

        if isinstance(msg, GameActionFightSpellImmunityMessage):
            gafsimsg = msg
            self.pushStep(FightSpellImmunityStep(gafsimsg.targetId))
            return True

        if isinstance(msg, GameActionFightKillMessage):
            gafkmsg = msg
            self.pushStep(FightKillStep(gafkmsg.targetId, gafkmsg.sourceId))
            return True

        if isinstance(msg, GameActionFightReduceDamagesMessage):
            gafredmsg = msg
            self.pushStep(FightReducedDamagesStep(gafredmsg.targetId, gafredmsg.amount))
            return True

        if isinstance(msg, GameActionFightReflectDamagesMessage):
            gafrfdmsg = msg
            self.pushStep(FightReflectedDamagesStep(gafrfdmsg.sourceId))
            return True

        if isinstance(msg, GameActionFightReflectSpellMessage):
            gafrsmsg = msg
            self.pushStep(FightReflectedSpellStep(gafrsmsg.targetId))
            return True

        if isinstance(msg, GameActionFightStealKamaMessage):
            gafskmsg = msg
            self.pushStep(FightStealingKamasStep(gafskmsg.sourceId, gafskmsg.targetId, gafskmsg.amount))
            return True

        if isinstance(msg, GameActionFightTackledMessage):
            gaftmsg = msg
            self.pushStep(FightTackledStep(gaftmsg.sourceId))
            return True

        if isinstance(msg, GameActionFightTriggerGlyphTrapMessage):
            if self._castingSpell:
                semsg = SequenceEndMessage()
                semsg.init(0, 0, 0)
                self._fightBattleFrame.process(semsg)
                self._fightBattleFrame.process(SequenceStartMessage())
                self._fightBattleFrame.currentSequenceFrame.process(msg)
                return True
            gaftgtmsg = msg
            self.fighterHasTriggeredGlyphOrTrap(gaftgtmsg)
            return True

        if isinstance(msg, GameActionFightActivateGlyphTrapMessage):
            gafagtmsg = msg
            self.pushStep(FightMarkActivateStep(gafagtmsg.markId, gafagtmsg.active))
            return True

        if isinstance(msg, GameActionFightDispellableEffectMessage):
            gaftbmsg = msg
            self.fighterHasBeenBuffed(gaftbmsg)
            return True

        if isinstance(msg, GameActionFightModifyEffectsDurationMessage):
            gafmedmsg = msg
            self.pushStep(FightModifyEffectsDurationStep(gafmedmsg.sourceId, gafmedmsg.targetId, gafmedmsg.delta))
            return False

        if isinstance(msg, GameActionFightCarryCharacterMessage):
            gafcchmsg = msg
            if gafcchmsg.cellId != -1:
                fightContextFrame_gafcchmsg = Kernel().fightContextFrame
                fightContextFrame_gafcchmsg.saveFighterPosition(gafcchmsg.targetId, gafcchmsg.cellId)
                carried = DofusEntities().getEntity(gafcchmsg.targetId)
                carriedByCarried = carried.carriedEntity
                while carriedByCarried:
                    fightContextFrame_gafcchmsg.saveFighterPosition(carriedByCarried.id, gafcchmsg.cellId)
                    carriedByCarried = carriedByCarried.carriedEntity
                self.pushStep(FightCarryCharacterStep(gafcchmsg.sourceId, gafcchmsg.targetId, gafcchmsg.cellId))
            return False

        if isinstance(msg, GameActionFightThrowCharacterMessage):
            gaftcmsg = msg
            throwCellId = (
                int(self._castingSpell.targetedCell.cellId)
                if self._castingSpell and self._castingSpell.targetedCell
                else int(gaftcmsg.cellId)
            )
            fightContextFrame_gaftcmsg = Kernel().fightContextFrame
            fightContextFrame_gaftcmsg.saveFighterPosition(gaftcmsg.targetId, throwCellId)
            self.pushThrowCharacterStep(gaftcmsg.sourceId, gaftcmsg.targetId, throwCellId)
            return False

        if isinstance(msg, GameActionFightDropCharacterMessage):
            gafdcmsg = msg
            dropCellId = gafdcmsg.cellId
            if dropCellId == -1 and self._castingSpell:
                dropCellId = self._castingSpell.targetedCell.cellId
            self.pushThrowCharacterStep(gafdcmsg.sourceId, gafdcmsg.targetId, dropCellId)
            return False

        if isinstance(msg, GameActionFightInvisibleDetectedMessage):
            gafidMsg = msg
            srcEntity = DofusEntities().getEntity(gafidMsg.sourceId)
            if not srcEntity:
                Logger().error("Source entity not found with dofus entities")
                srcEntity = FightEntitiesHolder().getEntity(gafidMsg.sourceId)
                if not srcEntity:
                    Logger().error("Source entity not found with fight entities holder!")
                    srcEntity = Kernel().fightEntitiesFrame.getEntityInfos(gafidMsg.sourceId)
                    if not srcEntity:
                        Logger().error("Source entity not found with fight entities!")
            self.pushStep(FightInvisibleTemporarilyDetectedStep(gafidMsg.sourceId, gafidMsg.cellId))
            Kernel().fightEntitiesFrame.setLastKnownEntityPosition(gafidMsg.targetId, gafidMsg.cellId)
            Kernel().fightEntitiesFrame.setLastKnownEntityMovementPoint(gafidMsg.targetId, 0)
            return True

        if isinstance(msg, GameFightTurnListMessage):
            gftmsg = msg
            self.pushStep(FightTurnListStep(gftmsg.ids, gftmsg.deadsIds))
            return True

        if isinstance(msg, AbstractGameActionMessage):
            Logger().error("Unsupported game action " + msg + " ! This action was discarded.")
            return True

        else:
            return False

    def execute(self, callback: FunctionType = None) -> None:
        self._sequencer = SerialSequencer(self.FIGHT_SEQUENCERS_CATEGORY)
        self._sequencer.on(SequencerEvent.SEQUENCE_STEP_FINISH, self.onStepEnd)
        if self._parent:
            self._parent.addSubSequence(self._sequencer)
        self.executeBuffer(callback)

    def fighterHasBeenKilled(self, gafdmsg: GameActionFightDeathMessage) -> None:
        summonDestroyedWithSummoner: bool = False
        summonerIsMe: bool = False
        entitiesDictionnary = Kernel().fightEntitiesFrame.entities
        for actorInfo in entitiesDictionnary.values():
            if isinstance(actorInfo, GameFightFighterInformations):
                if actorInfo.spawnInfo.alive and actorInfo.stats.summoner == gafdmsg.targetId:
                    self.pushStep(FightDeathStep(actorInfo.contextualId))
        playerId = PlayedCharacterManager().id
        Kernel().fightEntitiesFrame.getEntityInfos(gafdmsg.sourceId)
        targetInfos = Kernel().fightEntitiesFrame.getEntityInfos(gafdmsg.targetId)

        playerInfos = Kernel().fightEntitiesFrame.getEntityInfos(playerId)
        summonDestroyedWithSummoner = False
        summonerIsMe = True
        if (
            targetInfos
            and targetInfos.stats.summoned
            and not isinstance(targetInfos, GameFightFighterNamedInformations)
            and not isinstance(targetInfos, GameFightEntityInformation)
        ):
            summonerInfos = Kernel().fightEntitiesFrame.getEntityInfos(targetInfos.stats.summoner)
            summonDestroyedWithSummoner = summonerInfos is None or not summonerInfos.spawnInfo.alive
            summonerIsMe = summonerInfos is not None and summonerInfos == playerInfos
        if not summonDestroyedWithSummoner and summonerIsMe:
            Kernel().fightEntitiesFrame.addLastKilledAlly(targetInfos)
        entityDeathStepAlreadyInBuffer: bool = False

        for step in self._stepsBuffer:
            if isinstance(step, FightDeathStep) and step.entityId == gafdmsg.targetId:
                entityDeathStepAlreadyInBuffer = True
                break
        if not entityDeathStepAlreadyInBuffer:
            self.pushStep(FightDeathStep(gafdmsg.targetId))

        entityInfos: GameContextActorInformations = Kernel().fightEntitiesFrame.getEntityInfos(
            gafdmsg.targetId
        )
        currentPlayedFighterManager = CurrentPlayedFighterManager()
        if isinstance(entityInfos, GameFightMonsterInformations):
            summonedEntityInfos = entityInfos
            summonedEntityInfos.spawnInfo.alive = False
            if currentPlayedFighterManager.checkPlayableEntity(summonedEntityInfos.stats.summoner):
                monster = Monster.getMonsterById(summonedEntityInfos.creatureGenericId)
                if monster.useSummonSlot:
                    currentPlayedFighterManager.removeSummonedCreature(summonedEntityInfos.stats.summoner)
                if monster.useBombSlot:
                    currentPlayedFighterManager.removeSummonedBomb(summonedEntityInfos.stats.summoner)
                SpellWrapper.refreshAllPlayerSpellHolder(summonedEntityInfos.stats.summoner)
        elif isinstance(entityInfos, GameFightFighterInformations):
            fighterInfos = entityInfos
            fighterInfos.spawnInfo.alive = False
            if fighterInfos.stats.summoner != 0:
                if currentPlayedFighterManager.checkPlayableEntity(fighterInfos.stats.summoner):
                    currentPlayedFighterManager.removeSummonedCreature(fighterInfos.stats.summoner)
                    SpellWrapper.refreshAllPlayerSpellHolder(fighterInfos.stats.summoner)

    def fighterHasLeftBattle(self, gaflmsg: GameActionFightLeaveMessage) -> None:
        fightEntityFrame_gaflmsg = Kernel().fightEntitiesFrame
        entitiesL: dict = fightEntityFrame_gaflmsg.entities
        for gcaiL in entitiesL.values():
            if isinstance(gcaiL, GameFightFighterInformations):
                summonerIdL = gcaiL.stats.summoner
                if summonerIdL == gaflmsg.targetId:
                    self.pushStep(FightDeathStep(gcaiL.contextualId))
        self.pushStep(FightDeathStep(gaflmsg.targetId, False))
        entityInfosL = fightEntityFrame_gaflmsg.getEntityInfos(gaflmsg.targetId)
        if isinstance(entityInfosL, GameFightMonsterInformations):
            summonedEntityInfosL = entityInfosL
            currentPlayedFighterManager = CurrentPlayedFighterManager()
            if currentPlayedFighterManager.checkPlayableEntity(summonedEntityInfosL.stats.summoner):
                monster = Monster.getMonsterById(summonedEntityInfosL.creatureGenericId)
                if monster.useSummonSlot:
                    currentPlayedFighterManager.removeSummonedCreature(summonedEntityInfosL.stats.summoner)
                if monster.useBombSlot:
                    currentPlayedFighterManager.removeSummonedBomb(summonedEntityInfosL.stats.summoner)
        if entityInfosL and isinstance(entityInfosL, GameFightFighterInformations):
            fightEntityFrame_gaflmsg.removeSpecificKilledAlly(entityInfosL)

    def cellsHasBeenMarked(self, gafmcmsg: GameActionFightMarkCellsMessage) -> None:
        spellId: int = gafmcmsg.mark.markSpellId
        if self._castingSpell and self._castingSpell.spell and self._castingSpell.spell.id != 1750:
            self._castingSpell.markId = gafmcmsg.mark.markId
            self._castingSpell.markType = gafmcmsg.mark.markType
            self._castingSpell.casterId = gafmcmsg.sourceId
            spellGrade = gafmcmsg.mark.markSpellLevel
        else:
            tmpSpell = Spell.getSpellById(spellId)
            spellLevel = tmpSpell.getSpellLevel(gafmcmsg.mark.markSpellLevel)
            for effect in spellLevel.effects:
                if (
                    effect.effectId == ActionIds.ACTION_FIGHT_ADD_TRAP_CASTING_SPELL
                    or effect.effectId == ActionIds.ACTION_FIGHT_ADD_GLYPH_CASTING_SPELL
                    or effect.effectId == ActionIds.ACTION_FIGHT_ADD_GLYPH_CASTING_SPELL_ENDTURN
                ):
                    spellId = effect.parameter0
                    spellGrade = Spell.getSpellById(spellId).getSpellLevel(effect.parameter1).grade
        self.pushStep(
            FightMarkCellsStep(
                gafmcmsg.mark.markId,
                gafmcmsg.mark.markType,
                gafmcmsg.mark.cells,
                spellId,
                spellGrade,
                gafmcmsg.mark.markTeamId,
                gafmcmsg.mark.markimpactCell,
                gafmcmsg.sourceId,
            )
        )

    def fighterSummonMultipleEntities(
        self,
        gafmsmsg: GameActionFightMultipleSummonMessage,
        gffinfos: GameFightFighterInformations,
    ) -> GameFightFighterInformations:
        for summons in gafmsmsg.summons:
            for sum in summons.summons:
                if isinstance(summons.spawnInformation, SpawnCharacterInformation):
                    gffninfos = GameFightFighterNamedInformations()
                    gffninfos.init(
                        sum.informations.contextualId,
                        sum.informations.disposition,
                        summons.look,
                        sum,
                        summons.wave,
                        summons.stats,
                        None,
                        summons.spawnInformation,
                    )
                    gffinfos = gffninfos

                if isinstance(summons.spawnInformation, SpawnCompanionInformation):
                    gfeinfos = GameFightEntityInformation()
                    gfeinfos.init(
                        sum.informations.contextualId,
                        sum.informations.disposition,
                        summons.look,
                        sum,
                        summons.wave,
                        summons.stats,
                        None,
                        summons.spawnInformation.modelId,
                        summons.spawnInformation.level,
                        summons.spawnInformation,
                    )
                    gffinfos = gfeinfos

                if isinstance(summons.spawnInformation, SpawnMonsterInformation):
                    gfminfos = GameFightMonsterInformations()
                    gfminfos.init(
                        contextualId_=sum.informations.contextualId,
                        disposition_=sum.informations.disposition,
                        look_=summons.look,
                        spawnInfo_=sum,
                        wave_=summons.wave,
                        stats_=summons.stats,
                        previousPositions_=None,
                        creatureGenericId_=summons.spawnInformation.creatureGenericId,
                        creatureGrade_=summons.spawnInformation.creatureGrade,
                        creatureLevel_=1,
                    )
                    gffinfos = gfminfos

                if isinstance(summons.spawnInformation, SpawnScaledMonsterInformation):
                    gfsminfos = GameFightMonsterInformations()
                    gfsminfos.init(
                        contextualId_=sum.informations.contextualId,
                        disposition_=sum.informations.disposition,
                        look_=summons.look,
                        spawnInfo_=sum,
                        wave_=summons.wave,
                        stats_=summons.stats,
                        previousPositions_=None,
                        creatureGenericId_=summons.spawnInformation.creatureGenericId,
                        creatureGrade_=summons.spawnInformation.creatureGrade,
                    )
                    gffinfos = gfsminfos

                else:
                    gffinfos = GameFightFighterInformations()
                    gffinfos.init(
                        contextualId_=sum.informations.contextualId,
                        disposition_=sum.informations.disposition,
                        look_=summons.look,
                        spawnInfo_=sum,
                        wave_=summons.wave,
                        stats_=summons.stats,
                        previousPositions_=None,
                    )
                self.summonEntity(gffinfos, gafmsmsg.sourceId, gafmsmsg.actionId)
        return gffinfos

    def fighterSummonEntity(self, msg: GameActionFightSummonMessage) -> None:
        for summon in msg.summons:
            if (
                msg.actionId == ActionIds.ACTION_CHARACTER_ADD_ILLUSION_RANDOM
                or msg.actionId == ActionIds.ACTION_CHARACTER_ADD_ILLUSION_MIRROR
            ):
                fightEntities = Kernel().fightEntitiesFrame.entities
                for fighterId in fightEntities:
                    infos = Kernel().fightEntitiesFrame.getEntityInfos(fighterId)
                    if (
                        not Kernel().fightEntitiesFrame.entityIsIllusion(fighterId)
                        and hasattr(infos, "name")
                        and hasattr(summon, "name")
                        and getattr(infos, "name") == getattr(summon, "name")
                    ):
                        summon.stats.summoner = infos.contextualId
                        break
                gfsfrsmsg = GameFightShowFighterRandomStaticPoseMessage()
                gfsfrsmsg.init(summon)
                Kernel().fightEntitiesFrame.process(gfsfrsmsg)
                illusionCreature = DofusEntities().getEntity(summon.contextualId)
                if illusionCreature:
                    illusionCreature.visible = False
                self.pushStep(FightVisibilityStep(summon.contextualId, True))
            else:
                self.summonEntity(summon, msg.sourceId, msg.actionId)

    def fightersExchangedPositions(self, gafepmsg: GameActionFightExchangePositionsMessage) -> None:
        fightContextFrame = Kernel().fightContextFrame
        if not self.isSpellTeleportingToPreviousPosition():
            fightContextFrame.saveFighterPosition(gafepmsg.sourceId, gafepmsg.targetCellId)
        else:
            fightContextFrame.deleteFighterPreviousPosition(gafepmsg.sourceId)
        fightContextFrame.saveFighterPosition(gafepmsg.targetId, gafepmsg.targetCellId)
        self.pushStep(
            FightExchangePositionsStep(
                gafepmsg.sourceId,
                gafepmsg.casterCellId,
                gafepmsg.targetId,
                gafepmsg.targetCellId,
            )
        )

    def fighterHasBeenTeleported(self, gaftosmmsg: GameActionFightTeleportOnSameMapMessage) -> None:
        fightContextFrame = Kernel().fightContextFrame
        if not self.isSpellTeleportingToPreviousPosition():
            if not self._teleportThroughPortal:
                fightContextFrame.saveFighterPosition(gaftosmmsg.targetId, gaftosmmsg.cellId)
            else:
                fightContextFrame.saveFighterPosition(gaftosmmsg.targetId, gaftosmmsg.cellId)
        elif fightContextFrame.getFighterPreviousPosition(gaftosmmsg.targetId) == gaftosmmsg.cellId:
            fightContextFrame.deleteFighterPreviousPosition(gaftosmmsg.targetId)
        self.pushTeleportStep(gaftosmmsg.targetId, gaftosmmsg.cellId)
        self._teleportThroughPortal = False

    def fighterHasMoved(self, gmmmsg: GameMapMovementMessage) -> None:
        movementPath: MovementPath = MapMovementAdapter.getClientMovement(gmmmsg.keyMovements)
        movementPathCells: list[int] = movementPath.getCells()
        Logger().info(f"Fighter {gmmmsg.actorId} has moved following the path {movementPathCells}")
        movingEntity: IMovable = DofusEntities().getEntity(gmmmsg.actorId)
        if not movingEntity:
            return Logger().error("Moving entity not found")
        if movingEntity.id == gmmmsg.actorId:
            movingEntity.position.cellId = movementPath.end.cellId
        else:
            Logger().error(f"Got entity with unexpected id {movingEntity.id}")
        
        fightContextFrame = Kernel().fightContextFrame
        if not fightContextFrame:
            return Logger().error("FightContextFrame not found")
        else:
            for mpcell in movementPathCells[1:]:
                fightContextFrame.saveFighterPosition(gmmmsg.actorId, mpcell)
                carriedEntity: IMovable = movingEntity.carriedEntity
                while carriedEntity:
                    fightContextFrame.saveFighterPosition(carriedEntity.id, mpcell)
                    carriedEntity = carriedEntity.carriedEntity
        self.pushStep(FightEntityMovementStep(gmmmsg.actorId, movementPath))
        return True

    def fighterHasTriggeredGlyphOrTrap(self, gaftgtmsg: GameActionFightTriggerGlyphTrapMessage) -> None:
        triggeredSpellId: int = 0
        eid: EffectInstanceDice = None
        self.pushStep(FightMarkTriggeredStep(gaftgtmsg.triggeringCharacterId, gaftgtmsg.sourceId, gaftgtmsg.markId))
        self._castingSpell = CastingSpell()
        self._castingSpell.casterId = gaftgtmsg.sourceId
        triggeringCharacterInfos: GameFightFighterInformations = (
            Kernel().fightEntitiesFrame.getEntityInfos(gaftgtmsg.triggeringCharacterId)
        )
        triggeredCellId = triggeringCharacterInfos.disposition.cellId if triggeringCharacterInfos else -1
        mark: MarkInstance = MarkedCellsManager().getMarkDatas(gaftgtmsg.markId)
        if triggeredCellId != -1:
            if mark:
                for eid in mark.associatedSpellLevel.effects:
                    if (
                        mark.markType == GameActionMarkTypeEnum.GLYPH
                        and eid.effectId == ActionIds.ACTION_FIGHT_ADD_GLYPH_CASTING_SPELL
                        or mark.markType == GameActionMarkTypeEnum.TRAP
                        and eid.effectId == ActionIds.ACTION_FIGHT_ADD_TRAP_CASTING_SPELL
                    ):
                        triggeredSpellId = eid.parameter0
                if triggeredSpellId:
                    self._castingSpell.spell = Spell.getSpellById(triggeredSpellId)
                    self._castingSpell.spellRank = self._castingSpell.spell.getSpellLevel(
                        mark.associatedSpellLevel.grade
                    )
                    self._castingSpell.targetedCell = MapPoint.fromCellId(gaftgtmsg.markImpactCell)
                    if mark.markType == GameActionMarkTypeEnum.GLYPH:
                        self._castingSpell.defaultTargetGfxId = 1016
                    elif mark.markType == GameActionMarkTypeEnum.TRAP:
                        self._castingSpell.defaultTargetGfxId = 1017
                    self.pushPlaySpellScriptStep(
                        1,
                        gaftgtmsg.sourceId,
                        triggeredCellId,
                        self._castingSpell.spell.id,
                        self._castingSpell.spellRank.grade,
                    )
        if mark and mark.markType == GameActionMarkTypeEnum.PORTAL:
            self._teleportThroughPortal = True

    def fighterHasBeenBuffed(self, gaftbmsg: GameActionFightDispellableEffectMessage) -> None:
        actionId: int = 0
        myCastingSpell = None
        if GameDebugManager().buffsDebugActivated:
            e = Effect.getEffectById(gaftbmsg.actionId)
            description = ""
            if e != None:
                description = e.description
            Logger().debug(
                "\r[BUFFS DEBUG] New Buff '"
                + description
                + "' ("
                + str(gaftbmsg.actionId)
                + ") lanched by "
                + str(gaftbmsg.sourceId)
                + " sur "
                + str(gaftbmsg.effect.targetId)
                + " (uid "
                + str(gaftbmsg.effect.uid)
                + ", sort "
                + str(gaftbmsg.effect.spellId)
                + ", duration "
                + str(gaftbmsg.effect.turnDuration)
                + ", desenvoutable "
                + str(gaftbmsg.effect.dispelable)
                + ", buff parent "
                + str(gaftbmsg.effect.parentBoostUid)
                + ")"
            )
        for castedSpell in self._castingSpells:
            if castedSpell.spell.id == gaftbmsg.effect.spellId and castedSpell.casterId == gaftbmsg.sourceId:
                myCastingSpell = castedSpell
        if not myCastingSpell:
            if gaftbmsg.actionId == ActionIdProtocol.ACTION_CHARACTER_UPDATE_BOOST:
                myCastingSpell = CastingSpell(False)
            else:
                myCastingSpell = CastingSpell(self._castingSpell == None)
            if self._castingSpell:
                myCastingSpell.castingSpellId = self._castingSpell.castingSpellId
                if self._castingSpell.spell and self._castingSpell.spell.id == gaftbmsg.effect.spellId:
                    myCastingSpell.spellRank = self._castingSpell.spellRank
            myCastingSpell.spell = Spell.getSpellById(gaftbmsg.effect.spellId)
            myCastingSpell.casterId = gaftbmsg.sourceId
        buffEffect: AbstractFightDispellableEffect = gaftbmsg.effect
        buff: BasicBuff = BuffManager().makeBuffFromEffect(buffEffect, myCastingSpell, gaftbmsg.actionId)
        if isinstance(buff, StateBuff):
            sb = buff
            if sb.actionId == ActionIds.ACTION_FIGHT_DISABLE_STATE:
                step = FightLeavingStateStep(sb.targetId, sb.stateId, buff)
            else:
                step = FightEnteringStateStep(sb.targetId, sb.stateId, sb.effect.durationString, buff)
            if myCastingSpell != None:
                step.castingSpellId = myCastingSpell.castingSpellId
            self._stepsBuffer.append(step)
            if isinstance(buff, StatBuff):
                buff.isRecent = True
            if isinstance(buffEffect, FightTemporaryBoostEffect):
                actionId = gaftbmsg.actionId
                if (
                    actionId != ActionIds.ACTION_CHARACTER_MAKE_INVISIBLE
                    and actionId != ActionIdProtocol.ACTION_CHARACTER_UPDATE_BOOST
                    and actionId != ActionIds.ACTION_CHARACTER_CHANGE_LOOK
                    and actionId != ActionIds.ACTION_CHARACTER_CHANGE_COLOR
                    and actionId != ActionIds.ACTION_CHARACTER_ADD_APPEARANCE
                    and actionId != ActionIds.ACTION_FIGHT_SET_STATE
                ):
                    if GameDebugManager().detailedFightLog_showEverything:
                        buff.effect.visibleInFightLog = True
                    if GameDebugManager().detailedFightLog_showBuffsInUi:
                        buff.effect.visibleInBuffUi = True
                    self.pushStep(
                        FightTemporaryBoostStep(
                            gaftbmsg.effect.targetId,
                            buff.effect.description,
                            buff.effect.duration,
                            buff.effect.durationString,
                            buff.effect.visibleInFightLog,
                            buff,
                        )
                    )
                if actionId == ActionIds.ACTION_CHARACTER_BOOST_SHIELD:
                    self.pushStep(FightShieldPointsVariationStep(gaftbmsg.effect.targetId, buff))
            self.pushStep(FightDisplayBuffStep(buff))

    def logBuffer(self):
        bufferStepsNames = [_.__class__.__name__ for _ in self._stepsBuffer]
        Logger().debug(f"\r[SEQ DEBUG] Buffer {bufferStepsNames} of sequence #{self._instanceId}")

    def executeBuffer(self, callback: FunctionType) -> None:
        step: ISequencable = None
        removed: bool = False
        deathNumber: int = 0
        cleanedBuffer: list = []
        startStep = []
        endStep = []
        deathNumber = 0
        for i in range(len(self._stepsBuffer) - 1, -1, -1):
            if removed and step:
                step.clear()
            removed = True
            step = self._stepsBuffer[i]
            if isinstance(step, FightDeathStep):
                deathNumber += 1
            elif isinstance(step, FightActionPointsVariationStep):
                if step.voluntarlyUsed:
                    startStep.append(step)
                    removed = False
                    continue
            removed = False
            cleanedBuffer.insert(0, step)
        cleanedBuffer = startStep + cleanedBuffer + endStep
        for step in cleanedBuffer:
            self._sequencer.addStep(step)
        self.clearBuffer()
        if callback is not None and not self._parent:
            self._sequenceEndCallback = callback
            self._sequencer.once(SequencerEvent.SEQUENCE_END, self.onSequenceEnd)
        self._lastCastingSpell = self._castingSpell
        if not self._parent:
            if not self._subSequenceWaitingCount:
                self._sequencer.start()
        else:
            if callback is not None:
                callback()
            self._parent.subSequenceInitDone()

    def onSequenceEnd(self, evt_id, e: SequencerEvent=None) -> None:
        self._sequenceEndCallback()

    def onStepEnd(self, e, isEnd: bool = True) -> None:
        pass

    def subSequenceInitDone(self) -> None:
        self._subSequenceWaitingCount -= 1
        # Logger().debug(
        #     f"\r[STEPS DEBUG] sequence #{self._instanceId} has {self._subSequenceWaitingCount} subsequences waiting and {self._scriptInit} script init"
        # )
        # Logger().debug(f"\r[STEPS DEBUG] init subsequence isWaiting {self.isWaiting}, sequencer {self._sequencer}")
        if not self.isWaiting and self._sequencer and not self._sequencer.running:
            # Logger().warn("Sub sequence init end -- Run main sequence")
            self._sequencer.start()
        else:
            # Logger().warn(f"warning did not start sequener of sequence #{self._instanceId}")
            pass

    def pushTeleportStep(self, fighterId: float, destinationCell: int) -> None:
        if destinationCell != -1:
            step = FightTeleportStep(fighterId, MapPoint.fromCellId(destinationCell))
            if self.castingSpell != None:
                step.castingSpellId = self.castingSpell.castingSpellId
            self._stepsBuffer.append(step)

    def pushSlideStep(self, fighterId: float, startCell: int, endCell: int) -> None:
        if startCell < 0 or endCell < 0:
            return
        step: FightEntitySlideStep = FightEntitySlideStep(
            fighterId, MapPoint.fromCellId(startCell), MapPoint.fromCellId(endCell)
        )
        if self.castingSpell != None:
            step.castingSpellId = self.castingSpell.castingSpellId
        self._stepsBuffer.append(step)

    def pushPointsVariationStep(self, fighterId: float, actionId: int, delta: int) -> None:
        step: IFightStep = None
        if actionId in [
            ActionIdProtocol.ACTION_CHARACTER_ACTION_POINTS_USE,
            ActionIds.ACTION_CHARACTER_ACTION_POINTS_LOST,
            ActionIds.ACTION_CHARACTER_ACTION_POINTS_WIN,
        ]:
            step = FightActionPointsVariationStep(fighterId, delta, False)
        elif actionId in [
            ActionIdProtocol.ACTION_CHARACTER_MOVEMENT_POINTS_USE,
            ActionIds.ACTION_CHARACTER_MOVEMENT_POINTS_LOST,
            ActionIds.ACTION_CHARACTER_MOVEMENT_POINTS_WIN,
        ]:
            step = FightMovementPointsVariationStep(fighterId, delta, False)
        else:
            Logger().warn(f"Points variation with unsupported action ({actionId}), skipping.")
            return
        if self.castingSpell is not None:
            step.castingSpellId = self.castingSpell.castingSpellId
        self._stepsBuffer.append(step)

    def pushStep(self, step: AbstractSequencable) -> None:
        if self.castingSpell is not None:
            step.castingSpellId = self.castingSpell.castingSpellId
        # Logger().debug(
        #     f"[SEQ DEBUG] Push step of type {step.__class__.__name__} to buffer of sequence #{self._instanceId}"
        # )
        self._stepsBuffer.append(step)

    def pushPointsLossDodgeStep(self, fighterId: float, actionId: int, amount: int) -> None:
        step: IFightStep = None
        if actionId == ActionIdProtocol.ACTION_FIGHT_SPELL_DODGED_PA:
            step = FightActionPointsLossDodgeStep(fighterId, amount)
        elif actionId == ActionIdProtocol.ACTION_FIGHT_SPELL_DODGED_PM:
            step = FightMovementPointsLossDodgeStep(fighterId, amount)
        else:
            Logger().warn(f"Points dodge with unsupported action ({actionId}), skipping.")
            return
        if self.castingSpell is not None:
            step.castingSpellId = self.castingSpell.castingSpellId
        self._stepsBuffer.append(step)

    def pushPlaySpellScriptStep(
        self,
        fxScriptId: int,
        fighterId: float,
        cellId: int,
        spellId: int,
        spellRank: int,
        stepBuff: SpellScriptBuffer = None,
    ) -> FightPlaySpellScriptStep:
        step: FightPlaySpellScriptStep = FightPlaySpellScriptStep(
            fxScriptId,
            fighterId,
            cellId,
            spellId,
            spellRank,
            stepBuff if stepBuff else self,
        )
        if self.castingSpell is not None:
            step.castingSpellId = self.castingSpell.castingSpellId
        self._stepsBuffer.append(step)
        return step

    def pushThrowCharacterStep(self, fighterId: float, carriedId: float, cellId: int) -> None:
        step: FightThrowCharacterStep = FightThrowCharacterStep(fighterId, carriedId, cellId)
        if self.castingSpell is not None:
            step.castingSpellId = self.castingSpell.castingSpellId
            step.portals = self.castingSpell.portalMapPoints
            step.portalIds = self.castingSpell.portalIds
        self._stepsBuffer.append(step)

    def clearBuffer(self) -> None:
        self._stepsBuffer.clear()

    def isSpellTeleportingToPreviousPosition(self) -> bool:
        spellEffect: EffectInstanceDice = None
        if self.castingSpell and self.castingSpell.spellRank:
            for spellEffect in self.castingSpell.spellRank.effects:
                if spellEffect.effectId == ActionIds.ACTION_FIGHT_ROLLBACK_PREVIOUS_POSITION:
                    return True
        return False

    def summonEntity(self, entity: GameFightFighterInformations, sourceId: float, actionId: int) -> None:
        entityInfosS: GameContextActorInformations = None
        summonedEntityInfosS: GameFightMonsterInformations = None
        monsterS: Monster = None
        gfsgmsg = GameFightShowFighterMessage()
        gfsgmsg.init(entity)
        Kernel().worker.process(gfsgmsg)
        if ActionIdHelper.isRevive(actionId):
            Kernel().fightEntitiesFrame.removeLastKilledAlly(entity.spawnInfo.teamId)
        summonedCreature = DofusEntities().getEntity(entity.contextualId)
        if summonedCreature:
            summonedCreature.visible = False
        self.pushStep(FightSummonStep(sourceId, entity))
        isBomb: bool = False
        isCreature: bool = False
        summonedCharacterInfoS: GameFightCharacterInformations = None
        if actionId == ActionIds.ACTION_SUMMON_BOMB:
            isBomb = True
        else:
            entityInfosS = Kernel().fightEntitiesFrame.getEntityInfos(entity.contextualId)
            isBomb = False
            summonedEntityInfosS = entityInfosS
            if isinstance(summonedEntityInfosS, GameFightMonsterInformations):
                monsterS = Monster.getMonsterById(summonedEntityInfosS.creatureGenericId)
                if monsterS and monsterS.useBombSlot:
                    isBomb = True
                if monsterS and monsterS.useSummonSlot:
                    isCreature = True
            else:
                summonedCharacterInfoS = entityInfosS
        if isCreature or summonedCharacterInfoS:
            CurrentPlayedFighterManager().addSummonedCreature(sourceId)
        elif isBomb:
            CurrentPlayedFighterManager().addSummonedBomb(sourceId)
