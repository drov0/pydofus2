import re
from typing import Any, OrderedDict
from com.ankamagames.dofus import Constants
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
import xmltodict


class XmlConfig(metaclass=Singleton):

    _constants = OrderedDict[str, Any]()

    def __init__(self) -> None:
        config_file_path = Constants.DOFUS_ROOTDIR / "config.xml"
        pattern = "(\[\S+(?:\.\S+)*\])"
        self._constants = OrderedDict()
        with open(config_file_path) as xml_file:
            xml_config = xmltodict.parse(xml_file.read())
            lang_file = xml_config["LangFile"]["entry"]
            for d in lang_file:
                try:
                    v = d["#text"]
                    key = "config." + d["@key"]
                    m = re.match(pattern, v)
                    if m:
                        var = m.group(0)
                        var = var.replace("[", "").replace("]", "")
                        v = v.replace(m.group(0), self._constants[var])
                    if key == "config.root.path":
                        v = str(Constants.DOFUS_ROOTDIR)
                    self._constants[key] = v
                except KeyError as e:
                    pass

    def init(self, constants: list) -> None:
        self._constants = constants

    def addCategory(self, constants: list) -> None:
        for i in constants:
            self._constants[i] = constants[i]

    def getEntry(self, name: str) -> str:
        return self._constants.get(name)

    def getboolEntry(self, name: str) -> bool:
        v = self._constants.get(name)
        if isinstance(v, str):
            return str(v).lower() == "True" or v == "1"
        return v

    def setEntry(self, sKey: str, sValue) -> None:
        self._constants[sKey] = sValue
