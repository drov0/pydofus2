from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter

class EffectInstancestr(EffectInstance, IDataCenter):

    text:str

    def __init__(self):
        super().__init__()

    def clone(self) -> EffectInstance:
        o:EffectInstanceString = EffectInstancestr()
        o.rawZone = rawZone
        o.effectId = effectId
        o.duration = duration
        o.delay = delay
        o.text = self.text
        o.random = random
        o.group = group
        o.targetId = targetId
        o.targetMask = targetMask
        return o

    @property
    def parameter3(self) -> Object:
        return self.text

    def setParameter(self, paramIndex:int, value) -> None:
        if paramIndex == 3:
            self.text = str(value)


