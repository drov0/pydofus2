from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QColor, QBrush, QPainter
from pydofus2.com.ankamagames.atouin.AtouinConstants import AtouinConstants
from pydofus2.com.ankamagames.atouin.resources.adapters.ElementsAdapter import ElementsAdapter
from pydofus2.com.ankamagames.atouin.resources.adapters.MapsAdapter import MapsAdapter
from pydofus2.com.ankamagames.atouin.rtypes.AtouinOptions import AtouinOptions
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.resources.adapters.AdapterFactory import AdapterFactory
from pydofus2.com.ankamagames.jerakine.types.events.PropertyChangeEvent import PropertyChangeEvent
from PyQt5.QtCore import QPointF, QRect, Qt, pyqtSignal

class Atouin(metaclass=Singleton):
    DEFAULT_MAP_EXTENSION = "png"

    def __init__(self):
        self._worldContainer = QGraphicsScene()
        self._overlayContainer = QGraphicsScene()
        self._spMapContainer = QGraphicsScene()
        self._spGfxContainer = QGraphicsScene()
        self._spChgMapContainer = QGraphicsScene()
        self._worldMask = QGraphicsScene()
        self._currentZoom = 1
        self._zoomPosX = 0
        self._zoomPosY = 0
        self._movementListeners = []
        self._aSprites = []
        self._worldVisible = True

        # Creating a QPainter object for cursorUpdateSprite
        self._cursorUpdateSprite = QPainter()
        self._cursorUpdateSprite.setPen(QColor(0, 255, 0))
        self._cursorUpdateSprite.setBrush(QBrush(QColor(0, 255, 0)))
        self._cursorUpdateSprite.drawRect(0, 0, 6, 6)

        self._aoOptions:AtouinOptions = None

        AdapterFactory.addAdapter("ele", ElementsAdapter)
        AdapterFactory.addAdapter("dlm", MapsAdapter)


    def setDisplayOptions(self, ao: AtouinOptions):
        self._aoOptions = ao
        self._worldContainer = ao.container
        self._handler = ao.handler
        self._aoOptions.propertyChanged.connect(self.onPropertyChange)
        
        # Clearing the worldContainer
        for i in reversed(range(self._worldContainer.count())):
            self._worldContainer.itemAt(i).setParent(None)

        self._overlayContainer = QGraphicsScene()
        self._spMapContainer = QGraphicsScene()
        self._spChgMapContainer = QGraphicsScene()
        self._spGfxContainer = QGraphicsScene()
        self._worldMask = QGraphicsScene()

        # Add your onRollOutMapContainer and onRollOverMapContainer methods here
        # self._spMapContainer.mouseLeave.connect(self.onRollOutMapContainer)
        # self._spMapContainer.mouseEnter.connect(self.onRollOverMapContainer)

        self._worldContainer.addItem(self._spMapContainer)
        self._worldContainer.addItem(self._spChgMapContainer)
        self._worldContainer.addItem(self._worldMask)
        self._worldContainer.addItem(self._spGfxContainer)
        self._worldContainer.addItem(self._overlayContainer)

        # Replace FrustumManager with your actual class instance
        # FrustumManager().init(self._spChgMapContainer)

        self._worldContainer.setObjectName("worldContainer")
        self._spMapContainer.setObjectName("mapContainer")
        self._worldMask.setObjectName("worldMask")
        self._spChgMapContainer.setObjectName("chgMapContainer")
        self._spGfxContainer.setObjectName("gfxContainer")
        self._overlayContainer.setObjectName("overlayContainer")

        self.computeWideScreenBitmapWidth(ao.getOption("frustum"))
        self.setWorldMaskDimensions(AtouinConstants.WIDESCREEN_BITMAP_WIDTH)

        hideBlackBorderValue = self._aoOptions.getOption("hideBlackBorder")

        if not hideBlackBorderValue:
            self.setWorldMaskDimensions(StageShareManager.startWidth, 0, 0, 1, "blackBorder")
            self.getWorldMask("blackBorder", False).setEnabled(True)
        else:
            m = self.getWorldMask("blackBorder", False)
            if m:
                self._worldContainer.removeItem(m)

        self.setFrustrum(ao.getOption("frustum"))
        self.init()

    def onPropertyChange(self, e: PropertyChangeEvent):
        if e.propertyName == "hideBlackBorder":
            if not e.propertyValue:
                self.setWorldMaskDimensions(StageShareManager.startWidth, 0, 0, 1, "blackBorder")
                self.getWorldMask("blackBorder", False).setEnabled(True)
            else:
                m = self.getWorldMask("blackBorder", False)
                if m:
                    m.parentItem().removeFromGroup(m)

    def computeWideScreenBitmapWidth(self, frustum):
        RIGHT_GAME_MARGIN = int((AtouinConstants.ADJACENT_CELL_LEFT_MARGIN - 1) * AtouinConstants.CELL_WIDTH)
        LEFT_GAME_MARGIN = int((AtouinConstants.ADJACENT_CELL_RIGHT_MARGIN - 1) * AtouinConstants.CELL_WIDTH)
        MAP_IMAGE_WIDTH = AtouinConstants.CELL_WIDTH * AtouinConstants.MAP_WIDTH + AtouinConstants.CELL_WIDTH
        AtouinConstants.WIDESCREEN_BITMAP_WIDTH = MAP_IMAGE_WIDTH + RIGHT_GAME_MARGIN + LEFT_GAME_MARGIN;
        StageShareManager.stageLogicalBounds = QRect(-(AtouinConstants.WIDESCREEN_BITMAP_WIDTH - StageShareManager.startWidth) / 2, 0, AtouinConstants.WIDESCREEN_BITMAP_WIDTH, StageShareManager.startHeight);
