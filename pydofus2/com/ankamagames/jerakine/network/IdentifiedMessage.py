from pydofus2.com.ankamagames.jerakine.messages.Message import Message


class IdentifiedMessage(Message):
    def getMessageId() -> int:
        raise NotImplementedError("This method must be overriden")
