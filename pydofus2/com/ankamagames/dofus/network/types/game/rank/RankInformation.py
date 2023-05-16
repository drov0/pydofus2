from pydofus2.com.ankamagames.dofus.network.types.game.rank.RankMinimalInformation import RankMinimalInformation

class RankInformation(RankMinimalInformation):
    order: int
    gfxId: int
    modifiable: bool
    rights: list[int]
    def init(self, order_: int, gfxId_: int, modifiable_: bool, rights_: list[int], id_: int, name_: str):
        self.order = order_
        self.gfxId = gfxId_
        self.modifiable = modifiable_
        self.rights = rights_
        
        super().init(id_, name_)
    