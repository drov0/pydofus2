from pydofus2.com.ankamagames.jerakine.messages.Message import Message


class MovementRequestTimeoutMessage(Message):
    
    _msg: Message

    def __init__(self, msg: Message):
        super().__init__()
        self._msg = msg
        
    @property
    def msg(self) -> float:
        return self._msg
    
