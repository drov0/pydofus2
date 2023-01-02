from pydofus2.com.ankamagames.dofus.datacenter.alignments.AlignmentSide import AlignmentSide
from pydofus2.com.ankamagames.dofus.datacenter.effects.Effect import Effect
from pydofus2.com.ankamagames.dofus.datacenter.items.ItemType import ItemType
from pydofus2.com.ankamagames.dofus.datacenter.items.LegendaryPowerCategory import (
    LegendaryPowerCategory,
)
from pydofus2.com.ankamagames.dofus.datacenter.jobs.Job import Job
from pydofus2.com.ankamagames.dofus.datacenter.monsters.Monster import Monster
from pydofus2.com.ankamagames.dofus.datacenter.monsters.MonsterRace import MonsterRace
from pydofus2.com.ankamagames.dofus.datacenter.monsters.MonsterSuperRace import MonsterSuperRace
import pydofus2.com.ankamagames.dofus.datacenter.spells.Spell as spellmod
import pydofus2.com.ankamagames.dofus.datacenter.spells.SpellLevel as spellLevelmod
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.utils.display.spellZone.SpellShapeEnum import (
    SpellShapeEnum,
)

logger = Logger("Dofus2")


class EffectInstance(IDataCenter):

    UNKNOWN_NAME: str = "???"

    IS_DISPELLABLE: int = 1

    IS_DISPELLABLE_ONLY_BY_DEATH: int = 2

    IS_NOT_DISPELLABLE: int = 3

    UNDEFINED_CATEGORY: int = -2

    UNDEFINED_SHOW: int = -1

    UNDEFINED_DESCRIPTION: str = "undefined"

    effectUid: int

    baseEffectId: int

    effectId: int

    order: int

    targetId: int

    targetMask: str

    duration: int

    delay: int

    random: float

    group: int

    modificator: int

    trigger: bool

    triggers: str

    visibleInTooltip: bool = True

    visibleInBuffUi: bool = True

    visibleInFightLog: bool = True

    visibleOnTerrain: bool = True

    forClientOnly: bool = False

    dispellable: int = 1

    zoneSize: object = None

    zoneShape: int = None

    zoneMinSize: object = None

    zoneEfficiencyPercent: object = None

    zoneMaxEfficiency: object = None

    zoneStopAtTarget: object = None

    effectElement: int = None

    spellId: int = None

    _effectData: Effect = None

    _durationstrValue: int

    _delaystrValue: int

    _durationstr: str

    _bonusType: int = -2

    _oppositeId: int = -1

    _category: int = -2

    _description: str = UNDEFINED_DESCRIPTION

    _theoricDescription: str = "None"

    _descriptionForTooltip: str = "None"

    _theoricDescriptionForTooltip: str = "None"

    _showSet: int = -1

    _priority: int = 0

    _rawZone: str

    _theoricShortDescriptionForTooltip: str = "None"

    def __init__(self):
        super().__init__()

    @property
    def description(self) -> str:
        # if self._description == self.UNDEFINED_DESCRIPTION:
        #     if not self._effectData:
        #         self._effectData = Effect.getEffectById(self.effectId)
        #     if not self._effectData:
        #         self._description = None
        #         return None
        #     self._description = self.prepareDescription(self._effectData.description, self.effectId)
        return self._description

    @property
    def rawZone(self) -> str:
        return self._rawZone

    @rawZone.setter
    def rawZone(self, data: str) -> None:
        self._rawZone = data
        self.parseZone()

    @property
    def durationString(self) -> str:
        if not self._durationstr or self._durationstrValue != self.duration or self._delaystrValue != self.delay:
            self._durationstrValue = self.duration
            self._delaystrValue = self.delay
            self._durationstr = self.getTurnCountStr(False)
        return self._durationstr

    @property
    def category(self) -> int:
        if self._category == self.UNDEFINED_CATEGORY:
            if not self._effectData:
                self._effectData = Effect.getEffectById(self.effectId)
            self._category = int(self._effectData.category) if self._effectData else -1
        return self._category

    @property
    def bonusType(self) -> int:
        if self._bonusType == -2:
            if not self._effectData:
                self._effectData = Effect.getEffectById(self.effectId)
            self._bonusType = int(self._effectData.bonusType) if self._effectData else -2
        return self._bonusType

    @property
    def useInFight(self) -> bool:
        if not self._effectData:
            self._effectData = Effect.getEffectById(self.effectId)
        return self._effectData and self._effectData.useInFight

    @property
    def oppositeId(self) -> int:
        if self._oppositeId == -1:
            if not self._effectData:
                self._effectData = Effect.getEffectById(self.effectId)
            self._oppositeId = int(self._effectData.oppositeId) if self._effectData else -1
        return self._oppositeId

    @property
    def priority(self) -> int:
        if self._priority == 0:
            if not self._effectData:
                self._effectData = Effect.getEffectById(self.effectId)
            self._priority = int(self._effectData.effectPriority) if self._effectData else int(0)
        return self._priority

    def clone(self, o: "EffectInstance" = None) -> "EffectInstance":
        if o is None:
            o: EffectInstance = EffectInstance()
        o.zoneShape = self.zoneShape
        o.zoneSize = self.zoneSize
        o.zoneMinSize = self.zoneMinSize
        o.zoneEfficiencyPercent = self.zoneEfficiencyPercent
        o.zoneMaxEfficiency = self.zoneMaxEfficiency
        o.effectUid = self.effectUid
        o.effectId = self.effectId
        o.order = self.order
        o.duration = self.duration
        o.random = self.random
        o.group = self.group
        o.targetId = self.targetId
        o.targetMask = self.targetMask
        o.delay = self.delay
        o.triggers = self.triggers
        o.visibleInTooltip = self.visibleInTooltip
        o.visibleInBuffUi = self.visibleInBuffUi
        o.visibleInFightLog = self.visibleInFightLog
        o.visibleOnTerrain = self.visibleOnTerrain
        o.forClientOnly = self.forClientOnly
        o.dispellable = self.dispellable
        return o

    def add(self) -> "EffectInstance":
        return EffectInstance()

    @staticmethod
    def getItemTypeName(id: int) -> str:
        o: ItemType = ItemType.getItemTypeById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getMonsterName(id: int) -> str:
        o: Monster = Monster.getMonsterById(id)
        return o.name if not not o else I18n.getUiText("ui.effect.unknownMonster")

    @staticmethod
    def getMonsterGrade(pId: int, pGrade: int) -> str:
        m: Monster = Monster.getMonsterById(pId)
        return str(m.getMonsterGrade(pGrade).level) if not m else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getSpellName(id: int) -> str:
        o: spellmod.Spell = spellmod.Spell.getSpellById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getSpellLevelName(id: int) -> str:
        o: spellLevelmod.SpellLevel = spellLevelmod.SpellLevel.getLevelById(id)
        name: str = EffectInstance.getSpellName(o.spellId) if not o else EffectInstance.UNKNOWN_NAME
        return EffectInstance.getSpellName(o.spellId) if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getLegendaryPowerCategoryName(id: int) -> str:
        powerCategory: LegendaryPowerCategory = LegendaryPowerCategory.getLegendaryPowerCategoryById(id)
        return powerCategory.categoryName if not powerCategory else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getJobName(id: int) -> str:
        o: Job = Job.getJobById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getAlignmentSideName(id: int) -> str:
        o: AlignmentSide = AlignmentSide.getAlignmentSideById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getItemName(id: int) -> str:
        from pydofus2.com.ankamagames.dofus.datacenter.items.Item import Item

        o: Item = Item.getItemById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getMonsterSuperRaceName(id: int) -> str:
        o: MonsterSuperRace = MonsterSuperRace.getMonsterSuperRaceById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    @staticmethod
    def getMonsterRaceName(id: int) -> str:
        o: MonsterRace = MonsterRace.getMonsterRaceById(id)
        return o.name if not o else EffectInstance.UNKNOWN_NAME

    def parseZone(self) -> None:
        params: list = None
        if self.rawZone and len(self.rawZone):
            self.zoneShape = self.rawZone[0]
            params = self.rawZone[1:].split(",")
            if self.zoneShape == SpellShapeEnum.l:
                self.zoneMinSize = int(params[0])
                self.zoneSize = int(params[1])
                if len(params) > 2:
                    self.zoneEfficiencyPercent = int(params[2])
                    self.zoneMaxEfficiency = int(params[3])

                if len(params) == 5:
                    self.zoneStopAtTarget = int(params[4])
                return
            else:
                if len(params) > 0:
                    if params[0] == "":
                        self.zoneSize = 1
                    else:
                        self.zoneSize = int(params[0])

                elif len(params) == 2:
                    if SpellZone.hasMinSize(self.rawZone[:1]):
                        self.zoneMinSize = int(params[1])
                    else:
                        self.zoneEfficiencyPercent = int(params[1])

                elif len(params) == 3:
                    if SpellZone.hasMinSize(self.rawZone[:1]):
                        self.zoneMinSize = int(params[1])
                        self.zoneEfficiencyPercent = int(params[2])
                    else:
                        self.zoneEfficiencyPercent = int(params[1])
                        self.zoneMaxEfficiency = int(params[2])

                elif len(params) == 4:
                    self.zoneMinSize = int(params[1])
                    self.zoneEfficiencyPercent = int(params[2])
                    self.zoneMaxEfficiency = int(params[3])

                else:
                    self.zoneMinSize = 0
                    self.zoneEfficiencyPercent = None
                    self.zoneMaxEfficiency = None
        else:
            logger.error(f"Zone incorrect ({self.rawZone})")

    @property
    def parameter0(self):
        return None

    @parameter0.setter
    def parameter0(self, value):
        pass

    @property
    def parameter1(self):
        return None

    @property
    def parameter2(self):
        return None

    @property
    def parameter3(self):
        return None

    @property
    def parameter4(self):
        return None

    def forceDescriptionRefresh(self) -> None:
        self._description = self.UNDEFINED_DESCRIPTION
        self._theoricDescription = self.UNDEFINED_DESCRIPTION
