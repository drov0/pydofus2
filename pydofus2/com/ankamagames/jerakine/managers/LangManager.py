import re
from pydofus2.com.ankamagames.jerakine import JerakineConstants
from pydofus2.com.ankamagames.jerakine.managers.StoreDataManager import StoreDataManager
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import (
    ThreadSharedSingleton,
)


class LangManager(metaclass=ThreadSharedSingleton):
    KEY_LANG_INDEX = "langIndex"
    KEY_LANG_CATEGORY = "langCategory"
    KEY_LANG_VERSION = "langVersion"

    def __init__(self) -> None:
        
        self._parseReference = dict()
        self._aLang:dict[str, str] = StoreDataManager().getSetData(
            JerakineConstants.DATASTORE_LANG, self.KEY_LANG_INDEX, list()
        )
        self._aCategory = StoreDataManager().getSetData(
            JerakineConstants.DATASTORE_LANG, self.KEY_LANG_CATEGORY, list()
        )
        self._aVersion = StoreDataManager().getData(
            JerakineConstants.DATASTORE_LANG_VERSIONS, self.KEY_LANG_VERSION
        )
        self._aCategory = list()
        self._aVersion = StoreDataManager().getSetData(
            JerakineConstants.DATASTORE_LANG_VERSIONS, self.KEY_LANG_VERSION, list()
        )

    def replaceKey(self, sTxt: str, bReplaceDynamicReference=False):
        from pydofus2.com.ankamagames.jerakine.data.I18n import I18n

        if sTxt is not None and "[" in sTxt:
            reg = re.compile(r"(?<!\\)\[([^\]]*)\]")
            aKey = reg.findall(sTxt)
            if "\\[" in sTxt:
                sTxt = sTxt.replace("\\[", "[")
            for key in aKey:
                sKey = key[1:-1]
                if sKey[0] == "#":
                    if not bReplaceDynamicReference:
                        continue
                    sKey = sKey[1:]
                sNewVal = str(self._aLang.get(sKey, None))
                print(self._aLang.get(sKey, None), sKey)
                if sNewVal is None:
                    if int(sKey) > 0:
                        sNewVal = I18n.getText(int(sKey))
                    if I18n.hasUiText(sKey):
                        sNewVal = I18n.getUiText(sKey)
                    if sKey[0] == "~":
                        continue
                    if self._replaceErrorCallback is not None:
                        sNewVal = self._replaceErrorCallback(sKey)
                    if sNewVal is None:
                        sNewVal = "[" + sKey + "]"
                        aFind = self.getCategory(sKey)
                        if len(aFind) > 0:
                            print("Incorrect reference to the key [" + sKey + "] in : " + sTxt + " (could be " + " or ".join(aFind) + ")")
                        else:
                            print("Unknown reference to the key [" + sKey + "] in : " + sTxt)
                sTxt = sTxt.replace(key, sNewVal)
        return sTxt
    
    def getUntypedEntry(self, sKey):
        langData = StoreDataManager().getData(JerakineConstants.DATASTORE_LANG, self.KEY_LANG_INDEX)
        sEntry = langData.get(sKey, None)
        if sEntry is None:
            print("[Warning] LangManager : " + sKey + " is unknown")
            sEntry = "!" + sKey
        if sEntry is not None and isinstance(sEntry, str) and "[" in sEntry:
            sEntry = self.replaceKey(sEntry, True)
        return sEntry

    def getEntry(self, skey):
        return self.getUntypedEntry(skey)
    
    def getCategory(self, sCategory, matchSubCategories=True):
        aResult = {}
        for key in self._aLang.keys():
            if matchSubCategories:
                if key == sCategory or key.startswith(sCategory):
                    aResult[key] = self._aLang[key]
        return aResult

    def setEntry(self, sKey:str, sValue:str, sType:str=None):
        if not sType:
            self._aLang[sKey] = sValue
        else:
            sType = sType.upper()
            if sType == "STRING":
                self._aLang[sKey] = sValue
            elif sType == "NUMBER":
                self._aLang[sKey] = float(sValue)
            elif sType in ["UINT", "INT"]:
                self._aLang[sKey] = int(sValue, 10)
            elif sType == "BOOLEAN":
                self._aLang[sKey] = sValue.lower() == "true"
            elif sType == "ARRAY":
                self._aLang[sKey] = sValue.split(",")
            else:
                self._aLang[sKey] = globals()[sType](sValue)