import pydofus2.com.ankamagames.jerakine.network.parser.NetworkMessageClassDefinition as nmcd
from pydofus2.com.ankamagames.jerakine.logger.Logger import TraceLogger
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.ankamagames.jerakine.network.parser.ProtocolSpec import \
    ProtocolSpec
from pydofus2.com.ankamagames.jerakine.network.parser.TypeEnum import TypeEnum


class NetMsgDataField:
    TRACE = False

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

    @property
    def isDynamicObj(self):
        return self._spec.get("dynamicType")

    @property
    def isPrimitive(self):
        return TypeEnum(self._spec["typeId"]) != TypeEnum.OBJECT

    def getFieldTypeLength(self):
        l = self._spec.get("length")
        if l is None:
            lTypeId = self._spec.get("lengthTypeId")
            if lTypeId is not None:
                if self.TRACE:
                    TraceLogger().debug("field has length type id " + str(lTypeId))
                return self.readPrimitive(TypeEnum(lTypeId))
        return l

    def deserialize(self):
        self.length = self.getFieldTypeLength()
        if self.length is not None:
            return self.readVector()
        if self.isPrimitive:
            return self.readPrimitive()
        else:
            return self.readObject()

    def readPrimitive(self, typeId=None):
        if typeId is None:
            typeId = TypeEnum(self._spec["typeId"])
        dataReader = NetMsgDataField.dataReader.get(typeId)
        if dataReader is None:
            raise Exception(f"Type id {typeId} not found in known types ids")
        ret = getattr(self._raw, dataReader)()
        if self.TRACE:
            TraceLogger().debug(f"{self._spec['name']} : {TypeEnum(self._spec['typeId']).name} =  value is {ret}")
        return ret

    def readObject(self):
        className = self._spec["type"]
        if self.isDynamicObj:
            typeId = self._raw.readUnsignedShort()
            classSpec = ProtocolSpec.getTypeSpecById(typeId)
            className = classSpec["name"]
        if self.TRACE:
            TraceLogger().debug(className + " {")
        obj = nmcd.NetworkMessageClassDefinition(className, self._raw).deserialize()
        if self.TRACE:
            TraceLogger().debug("}")
        return obj

    def readVector(self):
        if self.TRACE:
            TraceLogger().debug("reading vector of length " + str(self.length))
        ret = []
        for i in range(self.length):
            if self.TRACE:
                TraceLogger().debug("------------------------------------------------")
                TraceLogger().debug("Reading vector element " + str(i))
            if self.isPrimitive:
                ret.append(self.readPrimitive())
            else:
                ret.append(self.readObject())
        return ret
