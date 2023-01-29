from pydofus2.com.ankamagames.dofus.logic.game.common.spell.SpellModifier import SpellModifier
from pydofus2.com.ankamagames.dofus.logic.game.common.spell.SpellModifiers import SpellModifiers
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterSpellModification import (
    CharacterSpellModification,
)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton


class SpellModifiersManager(metaclass=Singleton):

    DATA_STORE_CATEGORY: str = "ComputerModule_spellModifiersManager"

    DATA_STORE_KEY_IS_VERBOSE: str = "spellModifiersManagerIsVerbose"

    DEFAULT_IS_VERBOSE: bool = False

    def __init__(self):
        self._entitiesMap = dict()
        self._isVerbose = self.DEFAULT_IS_VERBOSE
        super().__init__()
        Logger().info("Instantiating spells manager")

    @property
    def isVerbose(self) -> bool:
        return self._isVerbose

    @isVerbose.setter
    def isVerbose(self, isVerbose: bool) -> None:
        if self._isVerbose == isVerbose:
            return
        self._isVerbose = isVerbose
        verboseAction: str = "enabled" if self._isVerbose else "disabled"
        Logger().info("Verbose mode has been " + verboseAction)

    def reset(self) -> None:
        Logger().info("Singleton instance has been destroyed")

    def setSpellModifiers(self, spellModifiers: SpellModifiers) -> bool:
        spellsModifierStats: dict = None
        if spellModifiers == None:
            Logger().error("Tried to set None spell modifier stats. Aborting")
            return False
        entityKey: str = str(spellModifiers.entityId)
        spellKey: str = str(spellModifiers.spellId)
        if entityKey not in self._entitiesMap:
            spellsModifierStats = self._entitiesMap[entityKey] = dict()
        else:
            spellsModifierStats = self._entitiesMap[entityKey]
        spellsModifierStats[spellKey] = spellModifiers
        return True

    def getSpellModifiers(self, entityId: float, spellId: float) -> SpellModifiers:
        entityKey: str = str(entityId)
        if entityKey not in self._entitiesMap:
            return None
        spellsModifierStats: dict = self._entitiesMap.get(entityKey)
        spellKey: str = str(spellId)
        if spellsModifierStats == None or spellKey not in spellsModifierStats:
            return None
        return spellsModifierStats[spellKey]

    def getSpellModifier(self, entityId: float, spellId: float, modifierId: float) -> SpellModifier:
        spellModifiers: SpellModifiers = self.getSpellModifiers(entityId, spellId)
        if spellModifiers is not None:
            return spellModifiers.getModifier(modifierId)
        return None

    def setRawSpellsModifiers(self, entityId: float, rawSpellsModifiers: list[CharacterSpellModification]) -> None:
        spellModifiers: SpellModifiers = None
        spellModifier: SpellModifier = None
        rawSpellModifier: CharacterSpellModification = None
        entityKey: str = str(entityId)
        spellsModifierStats: dict = dict()
        self._entitiesMap[entityKey] = dict()
        if rawSpellsModifiers is not None and len(rawSpellsModifiers) > 0:
            spellModifier = None
            for rawSpellModifier in rawSpellsModifiers:
                spellModifiers = spellsModifierStats.get(str(rawSpellModifier.spellId))
                if spellModifiers is None:
                    spellModifiers = SpellModifiers(entityId, rawSpellModifier.spellId)
                    self.setSpellModifiers(spellModifiers)
                spellModifier = SpellModifier(
                    rawSpellModifier.modificationType,
                    rawSpellModifier.value.base,
                    rawSpellModifier.value.additional,
                    rawSpellModifier.value.objectsAndMountBonus,
                    rawSpellModifier.value.alignGiftBonus,
                    rawSpellModifier.value.contextModif,
                )
                spellModifiers.setModifier(spellModifier)

    def setRawSpellModifier(self, entityId: float, rawSpellModifier: CharacterSpellModification) -> None:
        if rawSpellModifier == None:
            return
        entityKey: str = str(entityId)
        spellsModifierStats: dict = self._entitiesMap.get(entityKey)
        if spellsModifierStats == None:
            spellsModifierStats = self._entitiesMap[entityKey] = dict()
        spellKey: str = str(rawSpellModifier.spellId)
        spellModifiers: SpellModifiers = spellsModifierStats.get(spellKey)
        if spellModifiers == None:
            spellModifiers = spellsModifierStats[spellKey] = SpellModifiers(entityId, rawSpellModifier.spellId)
        spellModifier: SpellModifier = SpellModifier(
            rawSpellModifier.modificationType,
            rawSpellModifier.value.base,
            rawSpellModifier.value.additional,
            rawSpellModifier.value.objectsAndMountBonus,
            rawSpellModifier.value.alignGiftBonus,
            rawSpellModifier.value.contextModif,
        )
        spellModifiers.setModifier(spellModifier)

    def deleteSpellsModifiers(self, entityId: float) -> bool:
        key: str = str(entityId)
        if key not in self._entitiesMap:
            Logger().error(
                "Tried to del spells modifier stats for entity with ID " + key + ", but none were found. Aborting"
            )
            return False
        del self._entitiesMap[key]
        Logger().info("Spells modifiers for entity with ID " + key + " deleted")
        return True

    def deleteSpellModifiers(self, entityId: float, spellId: float) -> bool:
        entityKey: str = str(entityId)
        spellKey: str = str(spellId)
        if entityKey not in self._entitiesMap:
            Logger().error(
                "Tried to del spell "
                + spellKey
                + " modifiers for entity with ID "
                + entityKey
                + ", but no spells modifier stats were found. Aborting"
            )
            return False
        spellModifiers: SpellModifiers = self._entitiesMap[entityKey]
        if not spellModifiers or spellKey not in spellModifiers:
            Logger().error(
                "Tried to del spell "
                + spellKey
                + " modifiers for entity with ID "
                + entityKey
                + ", but none were found. Aborting"
            )
            return False
        del spellModifiers[spellKey]
        Logger().info("Spell " + spellKey + " modifiers for entity with ID " + entityKey + " deleted")
        return True
