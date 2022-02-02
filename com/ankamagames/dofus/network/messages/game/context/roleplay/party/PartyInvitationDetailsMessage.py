from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.AbstractPartyMessage import AbstractPartyMessage
from com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyInvitationMemberInformations import PartyInvitationMemberInformations
from com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyGuestInformations import PartyGuestInformations


@dataclass
class PartyInvitationDetailsMessage(AbstractPartyMessage):
    partyType:int
    partyName:str
    fromId:int
    fromName:str
    leaderId:int
    members:list[PartyInvitationMemberInformations]
    guests:list[PartyGuestInformations]
    
    
    def __post_init__(self):
        super().__init__()
    