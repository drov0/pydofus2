from pydofus2.com.ankamagames.dofus.network.messages.game.alliance.AllianceListMessage import AllianceListMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.social.AllianceFactSheetInformations import AllianceFactSheetInformations
    


class AlliancePartialListMessage(AllianceListMessage):
    

    def init(self, alliances_:list['AllianceFactSheetInformations']):
        
        super().init(alliances_)
    