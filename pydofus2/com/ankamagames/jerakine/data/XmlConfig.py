from collections import OrderedDict
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import re
from pydofus2.com.ankamagames.jerakine import JerakineConstants
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.managers.StoreDataManager import StoreDataManager
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton
import threading

lock = threading.Lock()
KEY_LANG_INDEX = "langIndex"

class XmlConfig(metaclass=ThreadSharedSingleton):
    _constants = OrderedDict[str, object]()
    _aLang = OrderedDict[str, str]()

    def __init__(self) -> None:
        from pydofus2.com.ankamagames.dofus import Constants

        config_file_path = Constants.DOFUS_ROOTDIR / "config.xml"
        pattern = "(\[\S+(?:\.\S+)*\])"
        tree = ET.parse(config_file_path)
        root = tree.getroot()
        for child in root:
            v = child.text
            key = "config." + child.attrib["key"]
            m = re.match(pattern, v)
            if m:
                var = m.group(0).replace("[", "").replace("]", "")
                if 'path' in var:
                    second_path_part = v.replace(m.group(0), "")
                    first_path_part = self._constants[var]
                    v = str(Path(os.path.join(first_path_part, second_path_part)))
                else:
                    v = v.replace(m.group(0), self._constants[var])
            if key == "config.root.path":
                v = str(Constants.DOFUS_ROOTDIR)
            self._constants[key] = v

    def init(self, constants: dict[str, object]) -> None:
        with lock:
            self._constants = constants

    def addCategory(self, constants: dict[str, object]) -> None:
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

    @property
    def entries(self):
        return self._constants

