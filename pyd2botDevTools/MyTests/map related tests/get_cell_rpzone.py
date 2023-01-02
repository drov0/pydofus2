from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager


currMapId = 90703364
currCell = 428
  
MapDisplayManager().loadMap(currMapId)
cell1 = MapDisplayManager().currentDataMap.cells[456]
cell2 = MapDisplayManager().currentDataMap.cells[544]

print(cell1)
print(cell2)