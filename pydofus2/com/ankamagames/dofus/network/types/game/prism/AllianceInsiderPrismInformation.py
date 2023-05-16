from pydofus2.com.ankamagames.dofus.network.types.game.prism.PrismInformation import PrismInformation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.data.items.ObjectItem import ObjectItem
    from pydofus2.com.ankamagames.dofus.network.types.game.data.items.ObjectItem import ObjectItem
    

class AllianceInsiderPrismInformation(PrismInformation):
    moduleObject: 'ObjectItem'
    moduleType: int
    cristalObject: 'ObjectItem'
    cristalType: int
    cristalEndDate: int
    cristalNumberLeft: int
    def init(self, moduleObject_: 'ObjectItem', moduleType_: int, cristalObject_: 'ObjectItem', cristalType_: int, cristalEndDate_: int, cristalNumberLeft_: int, state_: int, placementDate_: int, nuggetsCount_: int, durability_: int):
        self.moduleObject = moduleObject_
        self.moduleType = moduleType_
        self.cristalObject = cristalObject_
        self.cristalType = cristalType_
        self.cristalEndDate = cristalEndDate_
        self.cristalNumberLeft = cristalNumberLeft_
        
        super().init(state_, placementDate_, nuggetsCount_, durability_)
    