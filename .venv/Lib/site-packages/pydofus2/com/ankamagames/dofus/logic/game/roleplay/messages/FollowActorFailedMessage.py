from pydofus2.com.ankamagames.jerakine.messages.Message import Message


class FollowActorFailedMessage(Message):
    def __init__(self, actorId: int, cellId: int):
        self.actorId = actorId
        self.cellId = cellId
