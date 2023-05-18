import pydofus2.com.ankamagames.jerakine.network.parser.NetworkMessageClassDefinition as nmcd
from pydofus2.com.ankamagames.jerakine.logger.Logger import TraceLogger
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.parser.ProtocolSpec import \
    ProtocolSpec
from pydofus2.com.ankamagames.jerakine.network.parser.TypeEnum import TypeEnum


class NetMsgDataField:
    TRACE = True

    dataReader = {
        TypeEnum.INT: "readInt",
        TypeEnum.UNSIGNEDINT: "readUnsignedInt",
        TypeEnum.SHORT: "readShort",
        TypeEnum.UNSIGNEDSHORT: "readUnsignedShort",
        TypeEnum.BYTE: "readByte",
        TypeEnum.UNSIGNEDBYTE: "readUnsignedByte",
        TypeEnum.FLOAT: "readFloat",
        TypeEnum.DOUBLE: "readDouble",
        TypeEnum.BOOLEAN: "readBoolean",
        TypeEnum.VARINT: "readVarInt",
        TypeEnum.VARLONG: "readVarLong",
        TypeEnum.UTF: "readUTF",
        TypeEnum.VARUHSHORT: "readVarUhShort",
        TypeEnum.VARUHINT: "readVarUhInt",
        TypeEnum.VARSHORT: "readVarShort",
        TypeEnum.VARUHLONG: "readVarUhLong",
    }

    def __init__(self, spec: dict, raw: ByteArray):
        self._spec = spec
        self._raw = raw
        self._type = None
        self._length = None

    @property
    def name(self) -> str:
        return self._spec.get("name")

    @property
    def type(self) -> str:
        if not self._type:
            self._type = self._spec.get("type")
        return self._type

    @type.setter
    def type(self, newValue):
        self._type = newValue

    @property
    def length(self) -> int:
        if self._length is None:
            self._length = self._spec.get("length")
        return self._length
    
    @length.setter
    def length(self, val):
        if val < 0:
            raise ValueError(f"Vector length can't be assigned a negative value '{val}'")
        self._length = val
    
    @property
    def lengthTypeId(self) -> int:
        return self._spec.get("lengthTypeId")
    
    @property
    def isVector(self) -> bool:
        return self.length or self.lengthTypeId

    @property
    def hasDynamicType(self):
        return self._spec.get("dynamicType")

    @property
    def typeId(self) -> int:
        return self._spec.get("typeId")
    
    @property
    def isPrimitive(self):
        return TypeEnum(self.typeId) != TypeEnum.OBJECT

    @property
    def typename(self) -> str:
        return self._spec.get("typename")

    def deserialize(self):
        if self.isVector:
            return self.readVector()
        if self.isPrimitive:
            val = self.readPrimitive()
            if self.TRACE:
                TraceLogger().debug(f"Field {self.name} = {val}")
            return val
        else:
            return self.readObject()

    def readPrimitive(self, typeId=None):
        if typeId is None:
            typeId = TypeEnum(self.typeId)
        dataReader = NetMsgDataField.dataReader.get(typeId)
        if dataReader is None:
            raise Exception(f"TypeId '{typeId}' not found in known types ids")
        return getattr(self._raw, dataReader)()

    def readObject(self):
        if self.hasDynamicType:
            typeId = self._raw.readUnsignedShort()
            self.type = ProtocolSpec.getTypeSpecById(typeId).get("name")
            if self.type is None:
                raise Exception("Unable to parse dynamic type of field")
        obj = nmcd.NetworkMessageClassDefinition(self.type, self._raw).deserialize()
        return obj

    def readVector(self):
        if self.length is None:
            self.length = self.readPrimitive(TypeEnum(self.lengthTypeId))
            if self.TRACE:
                TraceLogger().debug(f"Read Vector length = {self.length}")
        if self.TRACE:
            TraceLogger().debug(f"==> Deserialising Vector<{self.typename}> of length {self.length}, remaining bytes {self._raw.remaining()}")
        ret = []
        for i in range(self.length):
            if self.isPrimitive:
                val = self.readPrimitive()
                if self.TRACE:
                    TraceLogger().debug(f"Vector value {i} = {val}")
                ret.append(val)
            else:
                if self.TRACE:
                    TraceLogger().debug(f"Reading Vector Object {i}.")
                ret.append(self.readObject())
        return ret
