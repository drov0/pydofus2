from dataclasses import dataclass
from com.ankamagames.dofus.network.types.common.basic.StatisticData import StatisticData


@dataclass
class StatisticDataShort(StatisticData):
    value:int
    
    
    def __post_init__(self):
        super().__init__()
    