from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.npc.TaxCollectorDialogQuestionExtendedMessage import TaxCollectorDialogQuestionExtendedMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.BasicNamedAllianceInformations import BasicNamedAllianceInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.BasicNamedAllianceInformations import BasicNamedAllianceInformations
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.BasicAllianceInformations import BasicAllianceInformations
    

class AllianceTaxCollectorDialogQuestionExtendedMessage(TaxCollectorDialogQuestionExtendedMessage):
    alliance: 'BasicNamedAllianceInformations'
    def init(self, alliance_: 'BasicNamedAllianceInformations', maxPods_: int, prospecting_: int, alliance_: 'BasicNamedAllianceInformations', taxCollectorsCount_: int, taxCollectorAttack_: int, pods_: int, itemsValue_: int, allianceInfo_: 'BasicAllianceInformations'):
        self.alliance = alliance_
        
        super().init(maxPods_, prospecting_, alliance_, taxCollectorsCount_, taxCollectorAttack_, pods_, itemsValue_, allianceInfo_)
    