from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapRunningFightDetailsMessage import MapRunningFightDetailsMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.party.NamedPartyTeam import NamedPartyTeam
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterLightInformations import GameFightFighterLightInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterLightInformations import GameFightFighterLightInformations
    

class MapRunningFightDetailsExtendedMessage(MapRunningFightDetailsMessage):
    namedPartyTeams: list['NamedPartyTeam']
    def init(self, namedPartyTeams_: list['NamedPartyTeam'], fightId_: int, attackers_: list['GameFightFighterLightInformations'], defenders_: list['GameFightFighterLightInformations']):
        self.namedPartyTeams = namedPartyTeams_
        
        super().init(fightId_, attackers_, defenders_)
    