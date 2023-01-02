from pydofus2.com.ankamagames.jerakine.messages.Message import Message


class FightRequestFailed(Message):
    def __init__(self, contextualId: int = None):
        self.actorId = contextualId
        super().__init__()
