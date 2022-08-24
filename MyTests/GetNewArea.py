from time import perf_counter
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.datacenter.world.SubArea import SubArea

currMapId = 88082952

  
# MapDisplayManager().loadMap(currMapId)
# subareaId = MapDisplayManager().currentDataMap.subareaId
# 

sa = SubArea.getSubAreaByMapId(currMapId)
areaId = sa._area.id
print(f"SubareaId: {sa.id}")
print(f"AreaId: {areaId}")
s = perf_counter()
print(sa.mapIds)
print(f"took: {perf_counter() - s}")
