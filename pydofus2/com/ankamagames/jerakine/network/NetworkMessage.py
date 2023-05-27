from types import FunctionType

import pydofus2.com.ankamagames.jerakine.network.parser.NetworkMessageClassDefinition as nmcd
import pydofus2.com.ankamagames.jerakine.network.parser.NetworkMessageEncoder as nmencoder
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import \
    INetworkMessage
from pydofus2.com.ankamagames.jerakine.network.parser.ProtocolSpec import \
    ProtocolSpec
from pydofus2.com.ankamagames.jerakine.network.utils.FuncTree import FuncTree


class NetworkMessage(INetworkMessage):

    GLOBAL_INSTANCE_ID: int = 0
    PACKET_ID_RIGHT_SHIFT: int = 2
    BIT_MASK: int = 3
    HASH_FUNCTION: FunctionType

    def __init__(self):
        NetworkMessage.GLOBAL_INSTANCE_ID = (NetworkMessage.GLOBAL_INSTANCE_ID + 1) % 1000
        self._instance_id = NetworkMessage.GLOBAL_INSTANCE_ID
        self.receptionTime: int = None
        self.sourceConnection: str = None
        self._name = None
        self._unpacked: bool = False
        super().__init__()

    def computeTypeLen(self, length: int) -> int:
        if length > 65535:
            return 3
        if length > 255:
            return 2
        if length > 0:
            return 1
        return 0

    def subComputeStaticHeader(self, msgId: int, typeLen: int) -> int:
        return msgId << self.PACKET_ID_RIGHT_SHIFT | typeLen

    @property
    def isInitialized(self) -> bool:
        raise Exception("Not implemented")

    @property
    def unpacked(self) -> bool:
        return self._unpacked

    @unpacked.setter
    def unpacked(self, value: bool) -> None:
        self._unpacked = value

    def writePacket(self, output: ByteArray, id: int, data: ByteArray) -> None:
        typeLen: int = len(self.computeTypeLen(data))
        output.writeShort(self.subComputeStaticHeader(id, typeLen))
        output.writeUnsignedInt(self._instance_id)
        if typeLen == 0:
            return
        elif typeLen == 1:
            output.writeByte(len(data))
        elif typeLen == 2:
            output.writeShort(len(data))
        elif typeLen == 3:
            high = len(data) >> 16 & 255
            low = len(data) & 65535
            output.writeByte(high)
            output.writeShort(low)
        output.writeByteArray(data, 0, len(data))

    def getMessageId(self) -> int:
        return ProtocolSpec.getProtocolIdByName(self.__class__.__name__)

    def getSpec(self) -> dict:
        return ProtocolSpec.getClassSpecByName(self.__class__.__name__)

    def reset(self) -> None:
        raise Exception("Not implemented")

    @classmethod
    def unpack(cls, data: ByteArray, length: int = None) -> "NetworkMessage":
        # Logger().debug(f"unpacking message of length {length}")
        if length is None:
            length = data.remaining()
        return nmcd.NetworkMessageClassDefinition(cls.__name__, data.read(length)).deserialize()

    def pack(self) -> ByteArray:
        data = nmencoder.NetworkMessageEncoder.encode(self)
        typelen = self.computeTypeLen(len(data))
        header = 4 * self.getMessageId() + typelen
        packed = ByteArray()
        packed.writeUnsignedShort(header)
        packed.writeUnsignedInt(self._instance_id)
        packed += len(data).to_bytes(typelen, "big")
        packed += data
        return packed

    def to_json(self) -> dict:
        return nmencoder.NetworkMessageEncoder.jsonEncode(self)

    @classmethod
    def from_json(cls, mjson: dict):
        return nmencoder.NetworkMessageEncoder.decodeFromJson(mjson)

    def unpackAsync(self, input: ByteArray, length: int) -> FuncTree:
        raise Exception("Not implemented")

    def readExternal(self, input: ByteArray) -> None:
        raise Exception("Not implemented")

    def writeExternal(self, output: ByteArray) -> None:
        raise Exception("Not implemented")

    def __eq__(self, __o: "NetworkMessage") -> bool:
        if __o is None:
            return False
        return self._instance_id == __o._instance_id

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __hash__(self) -> int:
        return self._instance_id

    def __str__(self) -> str:
        className: str = self.__class__.__name__
        return className.split(".")[-1] + " @" + str(self._instance_id)
    
    def __repr__(self) -> str:
        return self.__str__()
