from pydofus2.com.ankamagames.dofus.types.data.AnimFunData import AnimFunData


class AnimFunNpcData(AnimFunData):

    subAnimFunData: list["AnimFunNpcData"]

    def __init__(self):
        super().__init__()
