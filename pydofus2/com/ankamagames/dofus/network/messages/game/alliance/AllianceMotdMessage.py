from pydofus2.com.ankamagames.dofus.network.messages.game.social.SocialNoticeMessage import SocialNoticeMessage


class AllianceMotdMessage(SocialNoticeMessage):
    

    def init(self, content_:str, timestamp_:int, memberId_:int, memberName_:str):
        
        super().init(content_, timestamp_, memberId_, memberName_)
    