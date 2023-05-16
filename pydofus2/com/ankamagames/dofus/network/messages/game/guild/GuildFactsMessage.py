from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.social.GuildFactSheetInformations import GuildFactSheetInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.character.CharacterMinimalSocialPublicInformations import CharacterMinimalSocialPublicInformations
    

class GuildFactsMessage(NetworkMessage):
    infos: 'GuildFactSheetInformations'
    creationDate: int
    members: list['CharacterMinimalSocialPublicInformations']
    def init(self, infos_: 'GuildFactSheetInformations', creationDate_: int, members_: list['CharacterMinimalSocialPublicInformations']):
        self.infos = infos_
        self.creationDate = creationDate_
        self.members = members_
        
        super().__init__()
    