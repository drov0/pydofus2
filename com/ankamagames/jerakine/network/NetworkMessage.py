from types import FunctionType
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from com.ankamagames.jerakine.network.utils.FuncTree import FuncTree


class NetworkMessage(INetworkMessage):
   
   GLOBAL_INSTANCE_ID:int = 0
   
   BIT_RIGHT_SHIFT_LEN_PACKET_ID:int = 2
   
   BIT_MASK:int = 3
   
   HASH_FUNCTION:FunctionType


   def __init__(self):
      NetworkMessage.GLOBAL_INSTANCE_ID += 1
      self._instance_id = NetworkMessage.GLOBAL_INSTANCE_ID
      self._unpacked:bool = False
      self.receptionTime:int = None
      self.sourceConnection:str = None
      super().__init__()
   
   def computeTypeLen(self, length:int) -> int:
      if length > 65535:
         return 3
      if length > 255:
         return 2
      if length > 0:
         return 1
      return 0
   
   def subComputeStaticHeader(self, msgId:int, typeLen:int) -> int:
      return msgId << self.BIT_RIGHT_SHIFT_LEN_PACKET_ID | typeLen
   
   @property
   def isInitialized(self) -> bool:
      raise Exception("Not implemented")
   
   @property
   def unpacked(self) -> bool:
      return self._unpacked
   
   @unpacked.setter
   def unpacked(self, value:bool) -> None:
      self._unpacked = value
   
   def writePacket(self, output:ByteArray, id:int, data:ByteArray) -> None:
      typeLen:int = len(self.computeTypeLen(data))
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
      output.writeBytes(data, 0, len(data))
   
   def getMessageId(self) -> int:
      raise Exception("Not implemented")
   
   def reset(self) -> None:
      raise Exception("Not implemented")
   
   def pack(self, output:ByteArray) -> None:
      raise Exception("Not implemented")
   
   def unpack(self, input:ByteArray, length:int) -> None:
      raise Exception("Not implemented")
   
   def unpackAsync(self, input:ByteArray, length:int) -> FuncTree:
      raise Exception("Not implemented")
   
   def readExternal(self, input:ByteArray) -> None:
      raise Exception("Not implemented")
   
   def writeExternal(self, output:ByteArray) -> None:
      raise Exception("Not implemented")
   
   def __str__(self) -> str:
      className:str = self.__class__.__name__
      return className.split(".")[-1] + " @" + str(self._instance_id)
