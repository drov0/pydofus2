from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.social.SocialNoticeMessage import SocialNoticeMessage


@dataclass
class BulletinMessage(SocialNoticeMessage):
    lastNotifiedTimestamp:int
    
    
    def __post_init__(self):
        super().__init__()
    