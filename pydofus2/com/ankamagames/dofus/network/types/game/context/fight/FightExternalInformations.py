from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.FightTeamLightInformations import FightTeamLightInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.FightOptionsInformations import FightOptionsInformations
    

class FightExternalInformations(NetworkMessage):
    fightId: int
    fightType: int
    fightStart: int
    fightSpectatorLocked: bool
    fightTeams: 'FightTeamLightInformations'
    fightTeamsOptions: 'FightOptionsInformations'
    def init(self, fightId_: int, fightType_: int, fightStart_: int, fightSpectatorLocked_: bool, fightTeams_: 'FightTeamLightInformations', fightTeamsOptions_: 'FightOptionsInformations'):
        self.fightId = fightId_
        self.fightType = fightType_
        self.fightStart = fightStart_
        self.fightSpectatorLocked = fightSpectatorLocked_
        self.fightTeams = fightTeams_
        self.fightTeamsOptions = fightTeamsOptions_
        
        super().__init__()
    