import importlib
import os

import pydofus2.com.ankamagames.jerakine.network.NetworkMessage as bnm
import pydofus2.com.ankamagames.jerakine.network.parser.NetworkMessageDataField as nmdf
from pydofus2.com.ankamagames.jerakine.logger.Logger import TraceLogger
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.parser.BooleanByteWrapper import \
    boolByteWrapper
from pydofus2.com.ankamagames.jerakine.network.parser.ProtocolSpec import \
    ProtocolSpec


class NetworkMessageClassDefinition:
    TRACE = False
    
    def __init__(self, className: str, raw: ByteArray) -> None:
        if self.TRACE:
            TraceLogger().debug("Getting spec for {}".format(className))
        classSpec = ProtocolSpec.getClassSpecByName(className)
        self._parent = classSpec["parent"]
        self._fields = classSpec["fields"]
        self._boolfields = classSpec["boolfields"]
        modulePath = classSpec["package"]
        try:
            clsModule = globals()[modulePath]
        except:
            clsModule = importlib.import_module(modulePath)
        self._cls = getattr(clsModule, classSpec["name"])
        self.raw = raw

    def deserialize(self, childInstance: object = None) -> object:
        if childInstance is None:
            inst = self._cls()
        else:
            inst = childInstance

        if self.TRACE:
            TraceLogger().debug("------------------ Deserializing {} STARTED-----------------".format(self._cls.__name__))

        if self._parent is not None:
            if self.TRACE:
                TraceLogger().debug("Class has parent {}".format(self._parent))
            inst = NetworkMessageClassDefinition(self._parent, self.raw).deserialize(inst)
            if self.TRACE:
                TraceLogger().debug("End of parent deserialization")
                TraceLogger().debug("BytesArray positon: {}".format(self.raw.position))

        try:
            for field, value in self.readBooleans(self._boolfields, self.raw).items():
                if self.TRACE:
                    TraceLogger().debug("{} = {}".format(field, value))
                setattr(inst, field, value)
        except Exception as e:
            TraceLogger().debug(f"Remaining bytes in raw: {self.raw.remaining()}")
            TraceLogger().error(f"Error while reading boolean fields!")
            raise e

        for field in self._fields:
            attrib = field["name"]
            if field["optional"]:
                isProvided = self.raw.readByte()
                if not isProvided:
                    continue
            if self.TRACE:
                TraceLogger().debug(f"deserializing field {attrib}")
            try:
                value = nmdf.NetMsgDataField(field, self.raw).deserialize()
            except Exception as e:
                TraceLogger().debug(inst.__class__.__name__)
                TraceLogger().debug(self._fields)
                TraceLogger().error(str(e), exc_info=True)
                raise KeyboardInterrupt
            if self.TRACE:
                TraceLogger().debug(f"found value : {value}")
            setattr(inst, attrib, value)
        if self.TRACE:
            TraceLogger().debug("------------------ Deserializing {} ENDED---------------------".format(self._cls.__name__))

        if inst.__class__.__base__ == bnm.NetworkMessage:
            bnm.NetworkMessage.__init__(inst)

        return inst

    def to_json(self):
        pass

    @classmethod
    def readBooleans(cls, boolfields, raw: ByteArray):
        ans = {}
        n = len(boolfields)
        if n > 0:
            if cls.TRACE:
                TraceLogger().debug("Reading {} booleans".format(n))
                TraceLogger().debug(f"I need {n // 8} bytes")
                TraceLogger().debug(f"Remaining bytes in raw: {raw.remaining()}")
            if raw.remaining() < n // 8:
                raise Exception("Not enough bytes to read booleans")
            for i, var in enumerate(boolfields):
                if i % 8 == 0:
                    _box: int = raw.readByte()
                value = boolByteWrapper.getFlag(_box, i % 8)
                if cls.TRACE:
                    TraceLogger().debug(f"{var['name']} = {value}")
                ans[var["name"]] = value
        return ans
