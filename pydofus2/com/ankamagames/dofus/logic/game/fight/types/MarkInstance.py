from com.ankamagames.atouin.types.Selection import Selection
from com.ankamagames.dofus.datacenter.spells.Spell import Spell
from com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel


class MarkInstance:

    markCasterId: float

    markId: int

    markType: int

    associatedSpell: Spell

    associatedSpellLevel: SpellLevel

    selections: list[Selection]

    cells: list[int]

    teamId: int

    active: bool

    markImpactCellId: int
