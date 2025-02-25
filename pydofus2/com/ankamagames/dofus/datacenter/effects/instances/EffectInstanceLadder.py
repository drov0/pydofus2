from pydofus2.com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from pydofus2.com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceCreature import (
    EffectInstanceCreature,
)
from pydofus2.com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter


class EffectInstanceLadder(EffectInstanceCreature, IDataCenter):

    monsterCount: int

    def __init__(self):
        super().__init__()

    def clone(self) -> EffectInstance:
        o: EffectInstanceLadder = EffectInstanceLadder()
        o.rawZone = self.rawZone
        o.effectId = self.effectId
        o.duration = self.duration
        o.delay = self.delay
        o.monsterFamilyId = self.monsterFamilyId
        o.monsterCount = self.monsterCount
        o.random = self.random
        o.group = self.group
        o.targetId = self.targetId
        o.targetMask = self.targetMask
        return o

    @property
    def parameter0(self) -> object:
        return self.monsterFamilyId

    @property
    def parameter2(self) -> object:
        return self.monsterCount

    def setParameter(self, paramIndex: int, value) -> None:
        if paramIndex == 0:
            int(value)
        elif paramIndex == 2:
            self.monsterCount = int(value)
