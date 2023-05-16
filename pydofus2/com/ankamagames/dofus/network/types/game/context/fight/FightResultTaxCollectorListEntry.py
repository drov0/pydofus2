from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.FightResultFighterListEntry import FightResultFighterListEntry
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.BasicAllianceInformations import BasicAllianceInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.FightLoot import FightLoot
    

class FightResultTaxCollectorListEntry(FightResultFighterListEntry):
    allianceInfo: 'BasicAllianceInformations'
    def init(self, allianceInfo_: 'BasicAllianceInformations', id_: int, alive_: bool, outcome_: int, wave_: int, rewards_: 'FightLoot'):
        self.allianceInfo = allianceInfo_
        
        super().init(id_, alive_, outcome_, wave_, rewards_)
    