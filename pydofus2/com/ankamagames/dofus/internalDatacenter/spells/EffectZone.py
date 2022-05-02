from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance


class EffectZone:

    _effect: EffectInstance = EffectInstance()

    zoneSize: object = None

    zoneShape: int = None

    zoneMinSize: object = None

    zoneEfficiencyPercent: object = None

    zoneMaxEfficiency: object = None

    zoneStopAtTarget: object = None

    _targetMask: str = None

    def __init__(self, rawZone: str, targetMask: str):
        super().__init__()
        self._effect.rawZone = rawZone
        self.zoneSize = self._effect.zoneSize
        self.zoneShape = self._effect.zoneShape
        self.zoneMinSize = self._effect.zoneMinSize
        self.zoneEfficiencyPercent = self._effect.zoneEfficiencyPercent
        self.zoneMaxEfficiency = self._effect.zoneMaxEfficiency
        self.zoneStopAtTarget = self._effect.zoneStopAtTarget
        self._targetMask = targetMask

    @property
    def targetMask(self) -> str:
        return self._targetMask
