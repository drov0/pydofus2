import re
from typing import Any
from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellType import SpellType
from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellVariant import SpellVariant
from pydofus2.com.ankamagames.dofus.types.IdAccessors import IdAccessors
from pydofus2.com.ankamagames.jerakine.data.GameData import GameData
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel
logger = Logger("Dofus2")


class Spell(IDataCenter):

    MODULE: str = "Spells"

    def __init__(self):
        super().__init__()
        self._indexedParam: list = None
        self._indexedCriticalParam: list = None
        self.id: int = 0
        self.nameId: int = 0
        self.descriptionId: int = 0
        self.typeId: int = 0
        self.order: int = 0
        self.scriptParams: str = ""
        self.scriptParamsCritical: str = ""
        self.scriptId: int = None
        self.scriptIdCritical: int = None 
        self.iconId: int = None
        self.spellLevels = list[int]()
        self.useParamCache: bool = True
        self.verbose_cast: bool = False
        self.default_zone: str = "0"
        self.bypassSummoningLimit: bool = False
        self.canAlwaysTriggerSpells: bool = False
        self.adminName: str = ""
        self._name: str = ""
        self._description: str = ""
        self._spellLevels = list["SpellLevel"]()
        self._spellVariant: SpellVariant = None
        
    @classmethod
    def getSpellById(cls, id: int) -> "Spell":
        return GameData.getObject(cls.MODULE, id)

    @classmethod
    def getSpells(cls) -> list["Spell"]:
        return GameData.getObjects(cls.MODULE)

    idAccessors: IdAccessors = IdAccessors(getSpellById, getSpells)

    @property
    def name(self) -> str:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name

    @property
    def description(self) -> str:
        if not self._description:
            self._description = I18n.getText(self.descriptionId)
        return self._description

    @property
    def type(self) -> SpellType:
        return SpellType.getSpellTypeById(self.typeId)

    @property
    def spellVariant(self) -> SpellVariant:
        allSpellVariants: list = None
        variant: SpellVariant = None
        if self._spellVariant is None:
            allSpellVariants = SpellVariant.getSpellVariants()
            for variant in allSpellVariants:
                if self.id in variant.spellIds:
                    self._spellVariant = variant
                    return self._spellVariant
        return self._spellVariant

    def getSpellLevel(self, level: int):
        self.spellLevelsInfo
        index: int = 0
        if len(self.spellLevels) >= level and level > 0:
            index = level - 1
        return self._spellLevels[index]

    @property
    def spellLevelsInfo(self) -> list:
        from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel

        if not self._spellLevels or len(self._spellLevels) != len(self.spellLevels):
            levelCount = len(self.spellLevels)
            self._spellLevels = [None] * levelCount
            for i in range(levelCount):
                self._spellLevels[i] = SpellLevel.getLevelById(self.spellLevels[i])
        return self._spellLevels

    def getScriptId(self, critical: bool = False) -> int:
        if critical and self.scriptIdCritical:
            return self.scriptIdCritical
        return self.scriptId

    def getParamByName(self, name: str, critical: bool = False) -> Any:
        tmp: list = None
        tmp2: list = None
        param: str = None
        if critical and self.scriptParamsCritical and self.scriptParamsCritical != "None":
            if not self._indexedCriticalParam or not self.useParamCache:
                self._indexedCriticalParam = list()
                if self.scriptParamsCritical:
                    tmp = self.scriptParamsCritical.split(",")
                    for param in tmp:
                        tmp2 = param.split(":")
                        self._indexedCriticalParam[tmp2[0]] = self.getValue(tmp2[1])
            return self._indexedCriticalParam[name]
        if not self._indexedParam or not self.useParamCache:
            self._indexedParam = list()
            if self.scriptParams:
                tmp = self.scriptParams.split(",")
                for param in tmp:
                    tmp2 = param.split(":")
                    self._indexedParam[tmp2[0]] = self.getValue(tmp2[1])
        return self._indexedParam[name]

    def getValue(self, str: str) -> Any:
        regNum = "^[+-]?[0-9.]*$"
        m = re.fullmatch(regNum, str)
        if m:
            num = float(str)
            return 0 if num is None else num
        return str

    def __str__(self) -> str:
        return self.name + " (" + str(self.id) + ")"
