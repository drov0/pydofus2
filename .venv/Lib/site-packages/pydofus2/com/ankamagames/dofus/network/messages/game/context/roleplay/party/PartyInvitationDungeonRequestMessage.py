from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationRequestMessage import PartyInvitationRequestMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.common.AbstractPlayerSearchInformation import AbstractPlayerSearchInformation
    


class PartyInvitationDungeonRequestMessage(PartyInvitationRequestMessage):
    dungeonId:int
    

    def init(self, dungeonId_:int, target_:'AbstractPlayerSearchInformation'):
        self.dungeonId = dungeonId_
        
        super().init(target_)
    