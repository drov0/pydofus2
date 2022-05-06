from com.ankamagames.dofus.enums.ActionIds import ActionIds
from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceCreature import (
    EffectInstanceCreature,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceDate import (
    EffectInstanceDate,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceDice import (
    EffectInstanceDice,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceDuration import (
    EffectInstanceDuration,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceInteger import (
    EffectInstanceInteger,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceLadder import (
    EffectInstanceLadder,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceMinMax import (
    EffectInstanceMinMax,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceMount import (
    EffectInstanceMount,
)
from com.ankamagames.dofus.datacenter.effects.instances.EffectInstanceString import (
    EffectInstanceString,
)
from com.ankamagames.dofus.datacenter.items.IncarnationLevel import IncarnationLevel
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffect import (
    ObjectEffect,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectCreature import (
    ObjectEffectCreature,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectDate import (
    ObjectEffectDate,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectDice import (
    ObjectEffectDice,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectDuration import (
    ObjectEffectDuration,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectInteger import (
    ObjectEffectInteger,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectLadder import (
    ObjectEffectLadder,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectMinMax import (
    ObjectEffectMinMax,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectMount import (
    ObjectEffectMount,
)
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffectString import (
    ObjectEffectString,
)
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger("Dofus2")


class ObjectEffectAdapter:
    def __init__(self):
        super().__init__()

    @classmethod
    def fromNetwork(cls, oe: ObjectEffect) -> EffectInstance:
        if isinstance(oe, ObjectEffectDice) and oe.actionId == ActionIds.ACTION_INCARNATION:
            effect = EffectInstanceDate()
            effect.year = oe.param1
            effect.month = oe.param2 * 32768 + oe.diceConst
            level = 1
            while True:
                incLevel = IncarnationLevel.getIncarnationLevelByIdAndLevel(oe.param1, level)
                if incLevel:
                    floor = incLevel.requiredXp
                level += 1
                incLevelPlusOne = IncarnationLevel.getIncarnationLevelByIdAndLevel(oe.param1, level)
                if incLevelPlusOne:
                    nextFloor = incLevelPlusOne.requiredXp
                if nextFloor < effect.month and level < 51:
                    break
                level -= 1
            effect.day = level
            effect.hour = 0
            effect.minute = 0
        else:
            if isinstance(oe, ObjectEffectString):
                effect = EffectInstanceString()
                effect.text = oe.value
            if isinstance(oe, ObjectEffectInteger):
                effect = EffectInstanceInteger()
                effect.param3 = oe.value
            if isinstance(oe, ObjectEffectMinMax):
                effect = EffectInstanceMinMax()
                effect.min = oe.min
                effect.max = oe.max
            if isinstance(oe, ObjectEffectDice):
                effect = EffectInstanceDice()
                effect.diceNum = oe.param1
                effect.diceSide = oe.param2
                effect.param3 = oe.diceConst
            if isinstance(oe, ObjectEffectDate):
                effect = EffectInstanceDate()
                effect.year = oe.year
                effect.month = oe.month + 1
                effect.day = oe.day
                effect.hour = oe.hour
                effect.minute = oe.minute
            if isinstance(oe, ObjectEffectDuration):
                effect = EffectInstanceDuration()
                effect.days = oe.days
                effect.hours = oe.hours
                effect.minutes = oe.minutes
            if isinstance(oe, ObjectEffectLadder):
                effect = EffectInstanceLadder()
                effect.monsterFamilyId = oe.monsterFamilyId
                effect.monsterCount = oe.monsterCount
            if isinstance(oe, ObjectEffectCreature):
                effect = EffectInstanceCreature()
                effect.monsterFamilyId = oe.monsterFamilyId
            if isinstance(oe, ObjectEffectMount):
                effect = EffectInstanceMount()
                effect.id = oe.id
                effect.expirationDate = oe.expirationDate
                effect.model = oe.model
                effect.owner = oe.owner
                effect.name = oe.name
                effect.level = oe.level
                effect.sex = oe.sex
                effect.isRideable = oe.isRideable
                effect.isFecondationReady = oe.isFecondationReady
                effect.isFeconded = oe.isFeconded
                effect.reproductionCount = oe.reproductionCount
                effect.reproductionCountMax = oe.reproductionCountMax
                clientEffects = list[EffectInstanceInteger]()
                for serverEffect in oe:
                    intEffect = EffectInstanceInteger()
                    inteffect.param3 = servereffect.param3
                    intEffect.effectId = serverEffect.actionId
                    intEffect.duration = 0
                    clientEffects.append(intEffect)
                effect.effects = clientEffects
                effect.capacities = oe.capacities
            else:
                effect = EffectInstance()
        effect.effectId = oe.actionId
        effect.duration = 0
        return effect
