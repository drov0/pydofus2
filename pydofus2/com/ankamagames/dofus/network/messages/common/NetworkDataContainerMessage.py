from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import \
    NetworkMessage


class NetworkDataContainerMessage(NetworkMessage):
    
    def init(self):
        super().__init__()
        self._content: ByteArray
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        if isinstance(value, (bytes, bytearray)):
            self._content = ByteArray(value)
        elif isinstance(value, ByteArray):
            self._content = value
        else:
            raise TypeError("Invalid input type")