from com.ankamagames.dofus.datacenter.effects.Effect import Effect
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceDice import (
    EffectInstanceDice,
)
from com.ankamagames.dofus.logic.game.fight.types.BasicBuff import BasicBuff
from com.ankamagames.dofus.logic.game.fight.types.CastingSpell import CastingSpell
from com.ankamagames.dofus.network.types.game.actions.fight.FightTriggeredEffect import (
    FightTriggeredEffect,
)


class TriggeredBuff(BasicBuff):

    delay: int

    triggerCount: int

    def __init__(
        self,
        effect: FightTriggeredEffect = None,
        castingSpell: CastingSpell = None,
        actionId: int = 0,
    ):
        if effect:
            super().__init__(
                effect,
                castingSpell,
                actionId,
                effect.diceNum,
                effect.diceSide,
                effect.value,
            )
            self.initParam(effect.diceNum, effect.diceSide, effect.value)
            self.delay = effect.delay
            self._effect.delay = self.delay
            self.triggerCount = 0

    @property
    def diceNum(self):
        return self._effect.parameter0

    @property
    def diceSide(self):
        return self._effect.parameter1

    @property
    def value(self):
        return self._effect.parameter2

    def initParam(self, diceNum: int, diceSide: int, value: int) -> None:
        min: int = 0
        max: int = 0
        super().initParam(diceNum, diceSide, value)
        e: Effect = Effect.getEffectById(self.actionId)
        if e and e.forceMinMax and isinstance(self._effect, EffectInstanceDice):
            min = value + diceNum
            max = diceNum * diceSide + value
            if min == max:
                self.diceNum = min
                self.value = 0
                self.diceSide = 0
            elif min > max:
                self.diceNum = max
                self.diceSide = min
                self.value = 0
            else:
                self.diceNum = min
                self.diceSide = max
                self.value = 0

    def clone(self, id: int = 0) -> BasicBuff:
        tb: TriggeredBuff = TriggeredBuff()
        tb.id = self.uid
        tb.uid = self.uid
        tb.dataUid = self.dataUid
        tb.actionId = self.actionId
        tb.targetId = self.targetId
        tb.castingSpell = self.castingSpell
        tb.duration = self.duration
        tb.dispelable = self.dispelable
        tb.source = self.source
        tb.aliveSource = self.aliveSource
        tb.sourceJustReaffected = self.sourceJustReaffected
        tb.parentBoostUid = self.parentBoostUid
        tb.initParam(self.diceNum, self.diceSide, self.value)
        tb.delay = self.delay
        tb._effect.delay = self.delay
        return tb

    @property
    def active(self) -> bool:
        return self.delay > 0 or super().active

    @property
    def trigger(self) -> bool:
        return True

    def incrementDuration(self, delta: int, dispellEffect: bool = False) -> bool:
        if self.delay > 0 and not dispellEffect:
            if self.delay + delta >= 0:
                self.delay -= 1
                self.effect.delay -= 1
            else:
                delta += self.delay
                self.delay = 0
                self.effect.delay = 0
        if delta != 0:
            return super().incrementDuration(delta, dispellEffect)
        return True

    @property
    def unusableNextTurn(self) -> bool:
        return self.delay <= 1 and self.getUnuableNextTurn()
