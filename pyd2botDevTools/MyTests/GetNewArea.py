from time import perf_counter
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.datacenter.world.SubArea import SubArea

currMapId = 192415750.0

  
# MapDisplayManager().loadMap(currMapId)
# subareaId = MapDisplayManager().currentDataMap.subareaId
# 

sa = SubArea.getSubAreaByMapId(currMapId)
areaId = sa._area.id
print(f"SubareaId: {sa.id}")
print(f"AreaId: {areaId}")
print(f"SubAreaName: {sa.name}")
print(f"AreaName: {sa._area.name}")
s = perf_counter()
print(sa.mapIds)
print(f"took: {perf_counter() - s}")
