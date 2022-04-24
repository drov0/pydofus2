from com.ankamagames.atouin.data.map.Layer import Layer
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

currMapId = 190582787
MapDisplayManager().loadMap(currMapId)
r: MapPoint = MapDisplayManager().getIdentifiedElementPosition(513809)
print(r)

r = MapPoint.fromCellId(112)
print(r)
