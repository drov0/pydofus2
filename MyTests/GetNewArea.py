from time import perf_counter
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea

currMapId = 120062979  
MapDisplayManager().loadMap(currMapId)
subareaId = MapDisplayManager().currentDataMap.subareaId
print(f"SubareaId: {subareaId}")

sa = SubArea.getSubAreaById(subareaId)

s = perf_counter()
print(sa.mapIds)
print(f"took: {perf_counter() - s}")
