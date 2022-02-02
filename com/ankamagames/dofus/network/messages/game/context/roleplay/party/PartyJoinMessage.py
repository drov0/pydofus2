from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.AbstractPartyMessage import AbstractPartyMessage
from com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyMemberInformations import PartyMemberInformations
from com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyGuestInformations import PartyGuestInformations


@dataclass
class PartyJoinMessage(AbstractPartyMessage):
    partyType:int
    partyLeaderId:int
    maxParticipants:int
    members:list[PartyMemberInformations]
    guests:list[PartyGuestInformations]
    restricted:bool
    partyName:str
    
    
    def __post_init__(self):
        super().__init__()
    