from com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.jerakine.network.parser.NetworkMessageClassDefinition import (
    NetworkMessageClassDefinition,
)
from com.ankamagames.jerakine.network.parser.ProtocolSpec import ProtocolSpec

logger = Logger("Dofus2")


class Message:
    def __init__(self, m_id, data, count=None, from_client=None, src=None, dst=None):
        self.id = m_id
        self.raw = data
        self.count = count
        self.from_client = from_client
        self.src_ip = src
        self.dst_ip = dst

    def __str__(self):
        ans = str.format(
            "{}(m_id={}, data={}, count={})",
            self.__class__.__name__,
            self.id,
            self.raw,
            self.count,
        )
        return ans

    def __repr__(self):
        ans = self.__str__()
        return ans

    @staticmethod
    def readMessageLength(staticHeader: int, src: ByteArray) -> int:
        byteLenDynamicHeader: int = staticHeader & NetworkMessage.BIT_MASK
        messageLength: int = int.from_bytes(src.read(byteLenDynamicHeader), "big")
        return messageLength

    @staticmethod
    def getMessageId(firstOctet: int) -> int:
        return firstOctet >> NetworkMessage.BIT_RIGHT_SHIFT_LEN_PACKET_ID

    @classmethod
    def fromRaw(cls, buf: ByteArray, from_client: bool, src=None, dst=None):
        """Read a message from the buffer and empty the beginning of the buffer.
        msg fields spec:
             id      |   len     |   data
           1 bytes   |  1 bytes  |  len bytes
        """
        if not buf:
            return

        if buf.remaining() < 2:
            logger.debug(f"Not enough data to read the header, byte available : {buf.remaining()} (needed : 2)")
            return None

        staticHeader = buf.readUnsignedShort()
        id = Message.getMessageId(staticHeader)
        byteLenDynamicHeader = staticHeader & NetworkMessage.BIT_MASK
        count = None
        if from_client:
            if buf.remaining() >= 4:
                count = buf.readUnsignedInt()
            else:
                logger.debug(f"Not enough data to read the count, byte available : {buf.remaining()} (needed : 4)")
                return None
        if buf.remaining() >= byteLenDynamicHeader:
            lenData = Message.readMessageLength(staticHeader, buf)
            if buf.remaining() >= lenData:
                data = buf.read(lenData)
            else:
                logger.debug(
                    f"Not enough data to read the data, byte available : {buf.remaining()} (needed : {lenData})"
                )
                buf.position = 0
                return None
        else:
            logger.debug(
                f"Not enough data to read the data length, byte available : {buf.remaining()} (needed : {byteLenDynamicHeader})"
            )
            buf.position = 0
            return None

        if id == 2:
            newbuffer = ByteArray(data.readByteArray())
            newbuffer.uncompress()
            msg = Message.fromRaw(newbuffer, from_client)
            if not msg or newbuffer.remaining():
                raise Exception("Unable to parse Message")

        res = cls(m_id=id, data=data, count=count, from_client=from_client, src=src, dst=dst)
        buf.trim()
        return res

    @property
    def name(self):
        if not self.from_client:
            return MessageReceiver._messagesTypes[self.id].__name__
        else:
            return ProtocolSpec.getClassSpecById(self.id)["name"]

    def lenlenData(self):
        if len(self.raw) > 65535:
            return 3
        if len(self.raw) > 255:
            return 2
        if len(self.raw) > 0:
            return 1
        return 0

    def serialize(self) -> ByteArray:
        header = 4 * self.id + self.lenlenData()
        ans = ByteArray()
        ans.writeUnsignedShort(header)
        if self.count is not None:
            ans.writeUnsignedInt(self.count)
        ans += len(self.raw).to_bytes(self.lenlenData(), "big")
        ans += self.raw
        return ans

    @staticmethod
    def from_json(json, count=None, random_hash=True):
        type_name: str = json["__type__"]
        msg_type: dict = ProtocolSpec.getClassSpecByName(type_name)
        type_id: int = msg_type["protocolId"]
        raw = ProtocolSpec.write(type_name, json, random_hash=random_hash)
        return Message(type_id, raw, count)

    def deserialize(self):
        try:
            return NetworkMessageClassDefinition(self.name, self.raw).deserialize()
        except:
            with open("messageFail.bin", "wb") as f:
                f.write(self.serialize())
            raise
