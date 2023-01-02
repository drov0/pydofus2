from pydofus2.com.ankamagames.jerakine.messages.Message import Message

class FightEndingMessage(Message):

    def __init__(self):
        super().__init__()

    def init(self) -> 'FightEndingMessage':
        return self


