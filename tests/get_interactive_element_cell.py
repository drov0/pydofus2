# Get the interactive element cell data from its id 
# Each map has mulptiple layers of cells 
# On the ground layer you find interactive elements such as farmable resources
# To get the cell of an interactive element by its id 
# Get the ground layer of tha map, for that you can use Layer.LAYER_GROUND 
# Then loup throught the cells, each cell has a number of elemets(SoundElement or GraphicalElement)
# Match the elemet id with the interactive element id, then you can get the cell of the interactive element
from com.ankamagames.atouin.data.map.Layer import Layer, LayerCell
from com.ankamagames.atouin.data.map.Map import Map
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint


def getInteractiveElementCell(map: Map, interactiveElementId: int) -> LayerCell:
    for layer in map.layers:
        if layer.layerId == Layer.LAYER_GROUND:
            for cell in layer.cells:
                for element in cell.elements:
                    if element.id == interactiveElementId:
                        return cell
    return None

# Use the module MapPoint to get the interactive element position. 
# You first need to get the cell of the interactive element
def getInteractiveElementPosition(map: Map, interactiveElementId: int) -> MapPoint:
    cell = getInteractiveElementCell(map, interactiveElementId)
    if cell is None:
        return None
    return MapPoint.fromCellId(cell.cellId)

