from pydofus2.com.ankamagames.dofus.datacenter.effects.EffectInstance import \
    EffectInstance
from pydofus2.com.ankamagames.dofus.types.IdAccessors import IdAccessors
from pydofus2.com.ankamagames.jerakine.data.GameData import GameData
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.interfaces.IDataCenter import \
    IDataCenter


class Mount(IDataCenter):

    MODULE: str = "Mounts"

    id: int

    familyId: int

    nameId: int

    look: str

    certificateId: int

    effects: list[EffectInstance]

    _name: str

    def __init__(self):
        super().__init__()
        self._name = ""

    @classmethod
    def getMountById(cls, id: int) -> "Mount":
        return GameData().getObject(cls.MODULE, id)

    classmethod

    def getMounts(cls) -> list:
        return GameData().getObjects(cls.MODULE)

    idAccessors: IdAccessors = IdAccessors(getMountById, getMounts)

    @property
    def name(self) -> str:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name
