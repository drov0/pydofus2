from pydofus2.com.ankamagames.dofus.network.types.game.context.TaxCollectorStaticInformations import TaxCollectorStaticInformations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.AllianceInformations import AllianceInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.AllianceInformation import AllianceInformation
    

class TaxCollectorStaticExtendedInformations(TaxCollectorStaticInformations):
    allianceIdentity: 'AllianceInformations'
    def init(self, allianceIdentity_: 'AllianceInformations', firstNameId_: int, lastNameId_: int, allianceIdentity_: 'AllianceInformation', callerId_: int):
        self.allianceIdentity = allianceIdentity_
        
        super().init(firstNameId_, lastNameId_, allianceIdentity_, callerId_)
    