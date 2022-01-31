from ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.utils.dataMapProvider import DataMapProvider
from com.ankamagames.dofus.types.entities.animatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.types.positions.mapPoint import MapPoint

currMapId = 190054912
MapDisplayManager().loadMap(currMapId)
DataMapProvider.init(AnimatedCharacter)
mp = MapPoint.fromCellId(15)
print(DataMapProvider().pointMov(mp.x, mp.y))
print(DataMapProvider().pointWeight(mp.x, mp.y))