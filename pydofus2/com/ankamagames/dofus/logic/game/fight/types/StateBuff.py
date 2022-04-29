from com.ankamagames.dofus.datacenter.spells.SpellState import SpellState
from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import FightEventsHelper
from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import FightBattleFrame
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import FightEntitiesFrame
from com.ankamagames.dofus.logic.game.fight.managers.FightersStateManager import FightersStateManager
from com.ankamagames.dofus.logic.game.fight.miscs.ActionIdHelper import ActionIdHelper
from com.ankamagames.dofus.logic.game.fight.types.BasicBuff import BasicBuff
from com.ankamagames.dofus.logic.game.fight.types.CastingSpell import CastingSpell
from com.ankamagames.dofus.network.types.game.actions.fight.FightTemporaryBoostStateEffect import FightTemporaryBoostStateEffect
from com.ankamagames.dofus.network.types.game.context.fight.GameFightCharacterInformations import GameFightCharacterInformations
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import GameFightFighterInformations
from com.ankamagames.dofus.types.enums.EntityIconEnum import EntityIconEnum
from com.ankamagames.dofus.types.enums.SpellStateIconVisibilityMaskEnum import SpellStateIconVisibilityMaskEnum
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class StateBuff(BasicBuff):
    _statName:str

    _isSilent:bool = True

    _isDisplayTurnRemaining:bool = False

    _isVisibleInFightLog:bool = False

    stateId:int

    delta:int

    def __init__(self, effect:FightTemporaryBoostStateEffect = None, castingSpell:CastingSpell = None, actionId:int = 0):
        spellState:SpellState = None
        if effect:
            spellState = SpellState.getSpellStateById(effect.stateId)
            super().__init__(effect, castingSpell, actionId, None, None, effect.stateId)
            self._statName = ActionIdHelper.getActionIdStatName(actionId)
            self.stateId = effect.stateId
            self.delta = effect.delta
            self._isSilent = spellState.isSilent
            self._isDisplayTurnRemaining = spellState.displayTurnRemaining
            self._isVisibleInFightLog = self.effect.visibleInFightLog

    @property
    def type(self) -> String:
        return "StateBuff"

    @property
    def statName(self) -> String:
        return self._statName

    @property
    def isSilent(self) -> bool:
        return self._isSilent

    @property
    def isDisplayTurnRemaining(self) -> bool:
        return self._isDisplayTurnRemaining

    @property
    def isVisibleInFightLog(self) -> bool:
        return self._isVisibleInFightLog

    def onApplied(self) -> None:
        self.addBuffState()
        SpellWrapper.refreshAllPlayerSpellHolder(targetId)
        super().onApplied()

    def onRemoved(self) -> None:
        self.removeBuffState()
        SpellWrapper.refreshAllPlayerSpellHolder(targetId)
        super().onRemoved()

    def clone(self, id:int = 0) -> BasicBuff:
        sb:StateBuff = StateBuff()
        sb._statName = self._statName
        sb.stateId = self.stateId
        sb.id = uid
        sb.uid = uid
        sb.dataUid = dataUid
        sb.actionId = actionId
        sb.targetId = targetId
        sb.castingSpell = castingSpell
        sb.duration = duration
        sb.dispelable = dispelable
        sb.source = source
        sb.aliveSource = aliveSource
        sb.sourceJustReaffected = sourceJustReaffected
        sb.parentBoostUid = parentBoostUid
        sb.initParam(param1, param2, param3)
        return sb

    def addBuffState(self) -> None:
        statePreviouslyActivated:bool = FightersStateManager().hasState(targetId, self.stateId)
        FightersStateManager().addStateOnTarget(targetId, self.stateId, self.delta)
        stateActivated:bool = FightersStateManager().hasState(targetId, self.stateId)
        if not statePreviouslyActivated and stateActivated:
            self.addStateIcon()
        elif statePreviouslyActivated and not stateActivated:
            self.removeStateIcon()

    def removeBuffState(self) -> None:
        statePreviouslyActivated:bool = FightersStateManager().hasState(targetId, self.stateId)
        FightersStateManager().removeStateOnTarget(targetId, self.stateId, self.delta)
        stateActivated:bool = FightersStateManager().hasState(targetId, self.stateId)
        chatLog:bool = False
        fbf:FightBattleFrame = Kernel.getWorker().getFrame(FightBattleFrame) as FightBattleFrame
        if fbf and not fbf.executingSequence and fbf.deadFightersList.find(targetId) == -1 and not self.isSilent:
            chatLog = True
        if not stateActivated:
            self.removeStateIcon()
            if statePreviouslyActivated and chatLog and self._isVisibleInFightLog:
                FightEventsHelper.sendFightEvent(FightEventEnum.FIGHTER_LEAVING_STATE, [targetId, self.stateId], targetId, -1, False, 2)
        elif not statePreviouslyActivated and stateActivated:
            self.addStateIcon()
            if chatLog and self._isVisibleInFightLog:
                FightEventsHelper.sendFightEvent(FightEventEnum.FIGHTER_ENTERING_STATE, [targetId, self.stateId], targetId, -1, False, 2)

    def addStateIcon(self) -> None:
        fightEntitiesFrame:FightEntitiesFrame = None
        spellState:SpellState = SpellState.getSpellStateById(self.stateId)
        icon:str = spellState.icon
        if not icon or icon == "":
            return
        displayIcon:bool = self.displayIconForThisPlayer(spellState.iconVisibilityMask)
        if displayIcon:
            fightEntitiesFrame = FightEntitiesFrame.getCurrentInstance()
            if self._isDisplayTurnRemaining:
                fightEntitiesFrame.addEntityIcon(targetId, icon, EntityIconEnum.FIGHT_STATE_CATEGORY, 0, 0, self.duration)
            else:
                fightEntitiesFrame.addEntityIcon(targetId, icon, EntityIconEnum.FIGHT_STATE_CATEGORY)
            fightEntitiesFrame.forceIconUpdate(targetId)

    def updateTurnRemaining(self) -> None:
        spellState:SpellState = None
        icon:str = None
        if self._isDisplayTurnRemaining:
            spellState = SpellState.getSpellStateById(self.stateId)
            icon = spellState.icon
            if not icon or icon == "":
                return
            if self.displayIconForThisPlayer(spellState.iconVisibilityMask):
                FightEntitiesFrame.getCurrentInstance().updateTurnRemaining(self.targetId, icon, self.duration)

    def removeStateIcon(self) -> None:
        fightEntitiesFrame:FightEntitiesFrame = None
        spellState:SpellState = SpellState.getSpellStateById(self.stateId)
        icon:str = spellState.icon
        if not icon or icon == "":
            return
        displayIcon:bool = self.displayIconForThisPlayer(spellState.iconVisibilityMask)
        if displayIcon:
            fightEntitiesFrame = FightEntitiesFrame.getCurrentInstance()
            fightEntitiesFrame.removeIcon(targetId, icon)

    def displayIconForThisPlayer(self, iconVisibility:int) -> bool:
        playerInfos:GameFightFighterInformations = None
        casterInfos:GameFightFighterInformations = None
        playerBreed:int = 0
        summonerInfos:GameFightFighterInformations = None
        casterInfos2:GameFightFighterInformations = None
        displayIcon:bool = False
        playerId:float = PlayedCharacterManager().id
        if iconVisibility  == SpellStateIconVisibilityMaskEnum.ALL_VISIBILITY:
                displayIcon = True
        if iconVisibility  == SpellStateIconVisibilityMaskEnum.TARGET_VISIBILITY:
                if self.targetId == playerId:
                    displayIcon = True
        if iconVisibility  == SpellStateIconVisibilityMaskEnum.CASTER_VISIBILITY:
                if not castingSpell:
                if castingSpell.casterId == playerId:
                    displayIcon = True
                else:
                    casterInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(castingSpell.casterId)
                    if not casterInfos:
                    if casterInfos.stats.summoner == playerId:
                        displayIcon = True
                    playerBreed = PlayedCharacterManager().infos.breed
                    playerInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(playerId)
                    if not playerInfos:
                    if isinstance(casterInfos, GameFightCharacterInformations):
                        if casterInfos.spawnInfo.teamId == playerInfos.spawnInfo.teamId and casterInfos.breed == playerBreed:
                            displayIcon = True
                    else:
                        summonerInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(casterInfos.stats.summoner)
                        if isinstance(summonerInfos, GameFightCharacterInformations):
                            if summonerInfos.spawnInfo.teamId == playerInfos.spawnInfo.teamId and summonerInfos.breed == playerBreed:
                                displayIcon = True
        if iconVisibility  == SpellStateIconVisibilityMaskEnum.CASTER_ALLIES_VISIBILITY:
                if not castingSpell:
                if castingSpell.casterId == playerId:
                    displayIcon = True
                else:
                    casterInfos2 = FightEntitiesFrame.getCurrentInstance().getEntityInfos(castingSpell.casterId) as GameFightFighterInformations
                    if casterInfos2 and casterInfos2.stats.summoner == playerId:
                        displayIcon = True
                    playerInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(playerId) as GameFightFighterInformations
                    if not playerInfos:
                    if casterInfos2.spawnInfo.teamId == playerInfos.spawnInfo.teamId:
                        displayIcon = True
        return displayIcon


