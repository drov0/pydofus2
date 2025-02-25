from pydofus2.com.ankamagames.jerakine.data.AbstractDataManager import \
    AbstractDataManager
from pydofus2.com.ankamagames.jerakine.data.I18nFileAccessor import \
    I18nFileAccessor


class I18n(AbstractDataManager):
    
    def __init__(self):
        super().__init__()

    @classmethod
    def getText(cls, id: int, params: list = None, replace: str = "%") -> str:
        if not id:
            return None
        txt: str = I18nFileAccessor().getText(id)
        if txt is None or txt == "None":
            return "[UNKNOWN_TEXT_ID_" + str(id) + "]"
        return cls.replaceParams(txt, params, replace)

    @classmethod
    def getUnDiacriticalText(cls, id: int, params: list = None, replace: str = "%") -> str:
        if not id:
            return None
        txt: str = I18nFileAccessor().getUnDiacriticalText(id)
        if txt == None or txt == "None":
            return "[UNKNOWN_TEXT_ID_" + str(id) + "]"
        return I18n.replaceParams(txt, params, replace)

    @classmethod
    def getUiText(cls, textId: str, params: list = None, replace: str = "%") -> str:
        txt: str = I18nFileAccessor().getNamedText(textId)
        if txt == None or txt == "None":
            return "[UNKNOWN_TEXT_NAME_" + str(textId) + "]"
        return cls.replaceParams(txt, params, replace)

    @classmethod
    def hasUiText(cls, textId: str) -> bool:
        return I18nFileAccessor().hasNamedText(textId)

    @classmethod
    def replaceParams(cls, text: str, params: list, replace: str) -> str:
        if not params or not len(params):
            return text
        for i in range(1, len(params) + 1):
            text = text.replace(replace + str(i), str(params[i - 1]))
        return text
