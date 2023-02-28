from pydofus2.com.ankamagames.dofus.logic.game.common.spell.SpellModifier import SpellModifier
from pydofus2.com.ankamagames.dofus.logic.game.common.spell.SpellModifiers import SpellModifiers
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterSpellModification import (
    CharacterSpellModification,
)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton


class SpellModifiersManager(metaclass=ThreadSharedSingleton):

    DATA_STORE_CATEGORY: str = "ComputerModule_spellModifiersManager"

    DATA_STORE_KEY_IS_VERBOSE: str = "spellModifiersManagerIsVerbose"

    DEFAULT_IS_VERBOSE: bool = False

    def __init__(self):
        self._entitiesMap = dict()
        self._isVerbose = self.DEFAULT_IS_VERBOSE
        super().__init__()

    @property
    def isVerbose(self) -> bool:
        return self._isVerbose

    @isVerbose.setter
    def isVerbose(self, isVerbose: bool) -> None:
        if self._isVerbose == isVerbose:
            return
        self._isVerbose = isVerbose
        verboseAction = "enabled" if self._isVerbose else "disabled"
        Logger().info(f"Verbose mode has been {verboseAction}")

    def setSpellModifiers(self, spellModifiers: SpellModifiers) -> bool:
        if spellModifiers is None:
            return False
        entityId = float(spellModifiers.entityId)
        spellId = float(spellModifiers.spellId)
        if entityId not in self._entitiesMap:
            self._entitiesMap[entityId] = dict[str, SpellModifiers]()
        self._entitiesMap[entityId][spellId] = spellModifiers
        return True

    def getSpellModifiers(self, entityId: float, spellId: float) -> SpellModifiers:
        return self._entitiesMap.get(float(entityId), {}).get(float(spellId), None)
    
    def getSpellModifier(self, entityId: float, spellId: float, modifierId: float) -> SpellModifier:
        spellModifiers = self.getSpellModifiers(entityId, spellId)
        return spellModifiers.getModifier(modifierId) if spellModifiers else None

    def setRawSpellsModifiers(self, entityId: float, rawSpellsModifiers: list[CharacterSpellModification]) -> None:
        self._entitiesMap[float(entityId)] = dict()
        if rawSpellsModifiers is not None and len(rawSpellsModifiers) > 0:
            for rawSpellModifier in rawSpellsModifiers:
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
        if rawSpellModifier is None:
            return
        entityId = float(entityId)
        spellsModifierStats = self._entitiesMap.get(entityId)
        if spellsModifierStats is None:
            spellsModifierStats = self._entitiesMap[entityId] = dict()
        spellId = float(rawSpellModifier.spellId)
        spellModifiers = spellsModifierStats.get(spellId)
        if spellModifiers is None:
            spellModifiers = spellsModifierStats[spellId] = SpellModifiers(entityId, rawSpellModifier.spellId)
        spellModifier = SpellModifier(
            rawSpellModifier.modificationType,
            rawSpellModifier.value.base,
            rawSpellModifier.value.additional,
            rawSpellModifier.value.objectsAndMountBonus,
            rawSpellModifier.value.alignGiftBonus,
            rawSpellModifier.value.contextModif,
        )
        spellModifiers.setModifier(spellModifier)

    def deleteSpellsModifiers(self, entityId: float) -> bool:
        entityId = float(entityId)
        if entityId not in self._entitiesMap:
            Logger().error(
                f"Tried to del spells modifier stats for entity with ID {entityId}, but none were found. Aborting"
            )
            return False
        del self._entitiesMap[entityId]
        Logger().info(f"Spells modifiers for entity with ID {entityId} deleted")
        return True

    def deleteSpellModifiers(self, entityId: float, spellId: float) -> bool:
        entityKey = float(entityId)
        spellKey = float(spellId)
        if entityKey not in self._entitiesMap:
            Logger().error(
                f"Tried to del spell {spellKey}"
                + f" modifiers for entity with ID {entityKey}"
                + ", but no spells modifier stats were found. Aborting"
            )
            return False
        spellModifiers = self._entitiesMap[entityKey]
        if not spellModifiers or spellKey not in spellModifiers:
            Logger().error(
                f"Tried to del spell {spellKey}"
                + f" modifiers for entity with ID {entityKey}"
                + ", but none were found. Aborting"
            )
            return False
        del spellModifiers[spellKey]
        Logger().info(f"Spell {spellKey} modifiers for entity with ID {entityKey} deleted")
        return True
