from types import FunctionType
from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray


class RawDataParser:
    _messagesTypes = dict()

    def parse(self, data: ByteArray, msgId: int, msgLen: int) -> INetworkMessage:
        raise NotImplementedError()

    def parseAsync(self, data: ByteArray, messageId: int, msgLen: int, compute: FunctionType) -> INetworkMessage:
        raise NotImplementedError()

    def getUnpackMode(self, param1: int) -> int:
        raise NotImplementedError()
