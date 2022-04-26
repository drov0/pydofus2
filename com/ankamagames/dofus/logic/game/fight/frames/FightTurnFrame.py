import math
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.messages.EntityMovementCompleteMessage import EntityMovementCompleteMessage
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.common.managers.MapMovementAdapter import MapMovementAdapter
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import FightContextFrame
from com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import FightSpellCastFrame
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import CurrentPlayedFighterManager
from com.ankamagames.dofus.logic.game.fight.miscs.FightReachableCellsMaker import FightReachableCellsMaker
from com.ankamagames.dofus.logic.game.fight.miscs.TackleUtil import TackleUtil
from com.ankamagames.dofus.network.messages.game.chat.ChatClientMultiMessage import ChatClientMultiMessage
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementRequestMessage import GameMapMovementRequestMessage
from com.ankamagames.dofus.network.messages.game.context.GameMapNoMovementMessage import GameMapNoMovementMessage
from com.ankamagames.dofus.network.messages.game.context.ShowCellRequestMessage import ShowCellRequestMessage
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnFinishMessage import GameFightTurnFinishMessage
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnReadyRequestMessage import GameFightTurnReadyRequestMessage
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicsInformations import CharacterCharacteristicsInformations
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import GameFightFighterInformations
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.data.XmlConfig import XmlConfig
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.pathfinding.Pathfinding import Pathfinding
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.events.PropertyChangeEvent import PropertyChangeEvent
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath
from com.ankamagames.jerakine.types.positions.PathElement import PathElement
from damageCalculation.tools.StatIds import StatIds


class FightTurnFrame(Frame):

    SWF_LIB:str = XmlConfig().getEntry:("config.ui.skin").extend("assets_tacticmod.swf")

    TAKLED_CURSOR_NAME:str = "TackledCursor"

    logger = Logger(__name__)

    SELECTION_PATH:str = "FightMovementPath"

    SELECTION_END_PATH:str = "FightMovementEndPath"

    SELECTION_PATH_TACKLED:str = "FightMovementPathTackled"

    SELECTION_PATH_UNREACHABLE:str = "FightMovementPathUnreachable"

    SELECTION_MOVEMENT_AREA:str = "FightMovementArea"

    REMIND_TURN_DELAY:int = 15000

    _movementSelection:Selection

    _movementTargetSelection:Selection

    _movementSelectionTackled:Selection

    _movementSelectionUnreachable:Selection

    _movementAreaSelection:Selection

    _isRequestingMovement:bool

    _spellCastFrame:Frame

    _finishingTurn:bool

    _remindTurnTimeoutId:int

    _myTurn:bool

    _turnDuration:int

    _remainingDurationSeconds:int

    _lastCell:MapPoint

    _cursorData:LinkedCursorData = None

    _cells:list[int]

    _cellsTackled:list[int]

    _cellsUnreachable:list[int]

    _lastPath:MovementPath

    _intervalTurn:float

    _playerEntity:IEntity

    _currentFighterId:float

    _tackleByCellId:dict

    _turnFinishingNoNeedToRedrawMovement:bool = False

    _lastMP:int = 0

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGH

    @property
    def myTurn(self) -> bool:
        return self._myTurn

    @myTurn.setter
    def myTurn(self, b:bool) -> None:
        refreshTarget = b != self._myTurn
        monsterEndTurn = not self._myTurn
        self._finishingTurn = False
        self._currentFighterId = CurrentPlayedFighterManager().currentFighterId
        self._playerEntity = DofusEntities.getEntity(self._currentFighterId)
        self._turnFinishingNoNeedToRedrawMovement = False
        self._myTurn = b
        if b:
            self.startRemindTurn()
            self.drawMovementArea()
        else:
            self._isRequestingMovement = False
            if self._remindTurnTimeoutId != 0:
                clearTimeout(self._remindTurnTimeoutId)
            self.removePath()
            self.removeMovementArea()
        fcf:'FightContextFrame' = Kernel().getWorker().getFrame('FightContextFrame')
        if fcf:
            fcf.refreshTimelineOverEntityInfos()
        scf:'FightSpellCastFrame' = Kernel().getWorker().getFrame('FightSpellCastFrame')
        if scf:
            if monsterEndTurn:
                scf.drawRange()
            if refreshTarget:
                if scf:
                    scf.refreshTarget(True)
        if self._myTurn and not scf:
            self.drawPath()

    @property
    def turnDuration(self) -> int:
        return self._turnDuration
    
    @turnDuration.setter
    def turnDuration(self, v:int) -> None:
        self._turnDuration = v
        self._remainingDurationSeconds = math.floor(v / 1000)
        if self._intervalTurn:
            self.clearInterval(self._intervalTurn)
        self._intervalTurn = setInterval(self.onSecondTick, 1000)

    @property
    def lastPath(self) -> MovementPath:
        return self._lastPath

    @property
    def movementAreaSelection(self) -> Selection:
        return self._movementAreaSelection

    def freePlayer(self) -> None:
        self._isRequestingMovement = False

    def pushed(self) -> bool:
        Atouin().options.addEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
        OptionManager.getOptionManager("dofus").addEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
        StatsManager().addListenerToStat(StatIds.MOVEMENT_POINTS, self.onUpdateMovementPoints)
        return True

    def process(self, msg:Message) -> bool:
        if isinstance(msg, GameFightSpellCastAction):
                gfsca = msg
                if self._spellCastFrame != null:
                    Kernel().getWorker().removeFrame(self._spellCastFrame)
                self.removePath()
                if self._myTurn:
                    self.startRemindTurn()
                bf = Kernel().getWorker().getFrame(FightBattleFrame) as FightBattleFrame
                playerInformation = FightEntitiesFrame.getCurrentInstance().getEntityInfos(self._currentFighterId) as GameFightFighterInformations
                if bf and bf.turnsCount <= 1 or playerInformation and playerInformation.spawnInfo.alive:
                    Kernel().getWorker().addFrame(self._spellCastFrame = FightSpellCastFrame(gfsca.spellId))
                return True
        if isinstance(msg, CellClickMessage):
                ccmsg = msg
                if KeyPoll().isDown(Keyboard.ALTERNATE) and not Kernel().getWorker().contains(FightSpellCastFrame):
                    if Kernel().getWorker().contains(PointCellFrame):
                        PointCellFrame().cancelShow()
                    if DataMapProvider().pointMov(MapPoint.fromCellId(ccmsg.cellId).x, MapPoint.fromCellId(ccmsg.cellId).y, True):
                        scrmsg = ShowCellRequestMessage()
                        scrmsg.initShowCellRequestMessage(ccmsg.cellId)
                        ConnectionsHandler.getConnection().send(scrmsg)
                        ccmmsg = ChatClientMultiMessage()
                        ccmmsg.initChatClientMultiMessage(text, ChatActivableChannelsEnum.CHANNEL_TEAM)
                        ConnectionsHandler.getConnection().send(ccmmsg)
                else:
                    if not self.myTurn:
                        return False
                    self.askMoveTo(ccmsg.cell)
                return True
        if isinstance(msg, GameMapNoMovementMessage):
                if not self.myTurn:
                    return False
                self._isRequestingMovement = False
                self.removePath()
                return True
        if isinstance(msg, EntityMovementCompleteMessage):
                emcmsg = msg
                fcf = Kernel().getWorker().getFrame(FightContextFrame) as FightContextFrame
                if fcf:
                    fcf.refreshTimelineOverEntityInfos()
                if not self.myTurn:
                    return True
                if emcmsg.entity.id == self._currentFighterId:
                    self._isRequestingMovement = False
                    spellCastFrame = Kernel().getWorker().getFrame(FightSpellCastFrame)
                    if not spellCastFrame:
                        self.drawPath()
                    self.startRemindTurn()
                    if self._finishingTurn:
                        self.finishTurn()
                return True
        if isinstance(msg, GameFightTurnFinishAction):
                if not self.myTurn:
                    return False
                self._turnFinishingNoNeedToRedrawMovement = True
                entitiesFrame = Kernel().getWorker().getFrame(FightEntitiesFrame) as FightEntitiesFrame
                playerInfos = entitiesFrame.getEntityInfos(self._currentFighterId) as GameFightFighterInformations
                if self._remainingDurationSeconds > 0 and not playerInfos.stats.summoned:
                    basicTurnDuration = CurrentPlayedFighterManager().getBasicTurnDuration()
                    secondsToReport = math.floor(self._remainingDurationSeconds / 2)
                    if basicTurnDuration + secondsToReport > 60:
                        secondsToReport = 60 - basicTurnDuration
                    if secondsToReport > 0 and not AFKFightManager().isAfk:
                        KernelEventsManager().processCallback(ChatHookList.TextInformation, PatternDecoder.combine(I18n.getUiText("ui.fight.secondsAdded", [secondsToReport]), "n", secondsToReport <= 1, secondsToReport == 0), ChatActivableChannelsEnum.PSEUDO_CHANNEL_INFO, TimeManager().getTimestamp())
                    self._remainingDurationSeconds = 0
                    clearInterval(self._intervalTurn)
                imE = DofusEntities.getEntity(self._currentFighterId) as IMovable
                if not imE:
                    return True
                if imE.isMoving:
                    self._finishingTurn = True
                else:
                    self.finishTurn()
                return True
        if isinstance(msg, MapContainerRollOutMessage):
                self.removePath()
                return True
        if isinstance(msg, GameFightTurnReadyRequestMessage):
                self._turnFinishingNoNeedToRedrawMovement = True
                return False
        else:
                return False

    def pulled(self) -> bool:
        Atouin().options.removeEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
        OptionManager.getOptionManager("dofus").removeEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
        StatsManager().removeListenerFromStat(StatIds.MOVEMENT_POINTS, self.onUpdateMovementPoints)
        if self._remindTurnTimeoutId != 0:
            clearTimeout(self._remindTurnTimeoutId)
        if self._intervalTurn:
            clearInterval(self._intervalTurn)
        Atouin().cellOverEnabled = False
        self.removePath()
        self.removeMovementArea()
        Kernel().getWorker().removeFrame(self._spellCastFrame)
        return True

    def drawMovementArea(self) -> None:
        if self._turnFinishingNoNeedToRedrawMovement or not Dofus().options.getOption("showMovementArea"):
            if self._movementAreaSelection:
                self.removeMovementArea()
            return
        if not self._playerEntity or IMovable(self._playerEntity).isMoving:
            self.removeMovementArea()
            return
        playerPosition:MapPoint = self._playerEntity.position
        stats:EntityStats = CurrentPlayedFighterManager().getStats()
        if not stats:
            return
        movementPoints:int = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)
        self._lastMP = movementPoints
        entitiesFrame:FightEntitiesFrame = FightEntitiesFrame.getCurrentInstance()
        playerInfos:GameFightFighterInformations = entitiesFrame.getEntityInfos(self._playerEntity.id) as GameFightFighterInformations
        tackle:float = TackleUtil.getTackle(playerInfos, playerPosition)
        self._tackleByCellId = dict()
        self._tackleByCellId[playerPosition.cellId] = tackle
        mpLost:int = int(movementPoints * (1 - tackle) + 0.5)
        if mpLost < 0:
            mpLost = 0
        movementPoints -= mpLost
        if movementPoints == 0:
            self.removeMovementArea()
            return
        fightReachableCellsMaker:FightReachableCellsMaker = FightReachableCellsMaker(playerInfos)
        reachableCells:list[int] = fightReachableCellsMaker.reachableCells
        if len(reachableCells) == 0:
            self.removeMovementArea()
            return
        if not self._movementAreaSelection:
            self._movementAreaSelection = Selection()
            self._movementAreaSelection.renderer = ZoneDARenderer(PlacementStrataEnums.STRATA_AREA, 0.4, True)
            self._movementAreaSelection.color = PATH_COLOR
            SelectionManager().addSelection(self._movementAreaSelection, SELECTION_MOVEMENT_AREA)
        self._movementAreaSelection.zone = Custom(reachableCells)
        SelectionManager().update(SELECTION_MOVEMENT_AREA, self._playerEntity.position.cellId)

    def drawPath(self, cell:MapPoint = None) -> None:
        tackle:float = None
        firstObstacle:PathElement = None
        pe:PathElement = None
        i:int = 0
        j:int = 0
        pathLen:int = 0
        s:Selection = None
        cursorSprite:Sprite = None
        font:UserFont = None
        fontName:str = None
        textFormat:TextFormat = None
        effect:GlowFilter = None
        cellsToUse:list[int] = None
        orientation:int = 0
        self._cells = list[int]()
        self._cellsTackled = list[int]()
        self._cellsUnreachable = list[int]()
        if Kernel().getWorker().contains(FightSpellCastFrame):
            return
        if self._isRequestingMovement:
            return
        if not cell:
            if FightContextFrame.currentCell == -1:
                return
            cell = MapPoint.fromCellId(FightContextFrame.currentCell)
        if not self._playerEntity:
            self.removePath()
            return
        characteristics:CharacterCharacteristicsInformations = CurrentPlayedFighterManager().getCharacteristicsInformations()
        stats:EntityStats = CurrentPlayedFighterManager().getStats()
        mpLost:int = 0
        apLost:int = 0
        movementPoints:int = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)
        actionPoints:int = stats.getStatTotalValue(StatIds.ACTION_POINTS)
        if IMovable(self._playerEntity).isMoving or self._playerEntity.position.distanceToCell(cell) > movementPoints:
            self.removePath()
            return
        path:MovementPath = Pathfinding.findPath(DataMapProvider(), self._playerEntity.position, cell, False, False, True)
        if DataMapProvider().len(obstaclesCells) > 0 and (len(path.path) == 0 or len(path.path) > movementPoints):
            path = Pathfinding.findPath(DataMapProvider(), self._playerEntity.position, cell, False, False, False)
            if len(path.path) > 0:
                pathLen = len(path.path)
                for (i = 0 i < pathLen i += 1)
                    if DataMapProvider().obstaclesCells.find(path.path[i].cellId) != -1:
                        firstObstacle = path.path[i]
                        for (j = i + 1 j < pathLen j += 1)
                            self._cellsUnreachable.append(path.path[j].cellId)
                        self._cellsUnreachable.append(path.end.cellId)
                        path.end = firstObstacle.step
                        path.path = path.path.slice(0, i)
        if len(path.path) == 0 or len(path.path) > movementPoints:
            self.removePath()
            return
        self._lastPath = path
        isFirst:bool = True
        mpCount:int = 0
        lastPe:PathElement = None
        entitiesFrame:FightEntitiesFrame = Kernel().getWorker().getFrame(FightEntitiesFrame) as FightEntitiesFrame
        playerInfos:GameFightFighterInformations = entitiesFrame.getEntityInfos(self._playerEntity.id) as GameFightFighterInformations
        for each (pe in path.path)
            if isFirst:
                isFirst = False
            else:
                tackle = TackleUtil.getTackle(playerInfos, lastPe.step)
                mpLost += int((movementPoints - mpCount) * (1 - tackle) + 0.5)
                if mpLost < 0:
                    mpLost = 0
                apLost += int(actionPoints * (1 - tackle) + 0.5)
                if apLost < 0:
                    apLost = 0
                movementPoints = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS) - mpLost
                actionPoints = stats.getStatTotalValue(StatIds.ACTION_POINTS) - apLost
                if mpCount < movementPoints:
                    if mpLost > 0:
                        self._cellsTackled.append(pe.step.cellId)
                    else:
                        self._cells.append(pe.step.cellId)
                    mpCount += 1
                else:
                    self._cellsUnreachable.append(pe.step.cellId)
            lastPe = pe
        tackle = TackleUtil.getTackle(playerInfos, lastPe.step)
        mpLost += int((movementPoints - mpCount) * (1 - tackle) + 0.5)
        if mpLost < 0:
            mpLost = 0
        apLost += int(actionPoints * (1 - tackle) + 0.5)
        if apLost < 0:
            apLost = 0
        movementPoints = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS) - mpLost
        if mpCount < movementPoints:
            if firstObstacle:
                movementPoints = len(path.path)
            if mpLost > 0:
                self._cellsTackled.append(path.end.cellId)
            else:
                self._cells.append(path.end.cellId)
        elif firstObstacle:
            self._cellsUnreachable.unshift(path.end.cellId)
            movementPoints = len(path.path) - 1
        else:
            self._cellsUnreachable.append(path.end.cellId)
        if self._movementSelection == null:
            self._movementSelection = Selection()
            self._movementSelection.renderer = MovementZoneRenderer(Dofus().options.getOption("showMovementDistance"))
            self._movementSelection.color = PATH_COLOR
            SelectionManager().addSelection(self._movementSelection, SELECTION_PATH)
            self._movementTargetSelection = Selection()
            self._movementTargetSelection.renderer = ZoneClipRenderer(!not Atouin().options.getOption("transparentOverlayMode") ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA), SWF_LIB, [], -1, False, False)
            SelectionManager().addSelection(self._movementTargetSelection, SELECTION_END_PATH)
        if len(self._cellsTackled) > 0:
            if self._movementSelectionTackled == null:
                self._movementSelectionTackled = Selection()
                self._movementSelectionTackled.renderer = MovementZoneRenderer(Dofus().options.getOption("showMovementDistance"))
                self._movementSelectionTackled.color = PATH_TACKLED_COLOR
                SelectionManager().addSelection(self._movementSelectionTackled, SELECTION_PATH_TACKLED)
            else:
                self._movementSelectionTackled.renderer.startAt = movementPoints + 1
            self._movementSelectionTackled.zone = Custom(self._cellsTackled)
            SelectionManager().update(SELECTION_PATH_TACKLED)
        else:
            s = SelectionManager().getSelection(SELECTION_PATH_TACKLED)
            if s:
                s.remove()
                self._movementSelectionTackled = None
        if len(self._cellsUnreachable) > 0:
            if self._movementSelectionUnreachable == null:
                self._movementSelectionUnreachable = Selection()
                self._movementSelectionUnreachable.renderer = MovementZoneRenderer(Dofus().options.getOption("showMovementDistance"), movementPoints + 1)
                self._movementSelectionUnreachable.color = PATH_UNREACHABLE_COLOR
                SelectionManager().addSelection(self._movementSelectionUnreachable, SELECTION_PATH_UNREACHABLE)
            else:
                self._movementSelectionUnreachable.renderer.startAt = movementPoints + 1
            self._movementSelectionUnreachable.zone = Custom(self._cellsUnreachable)
            SelectionManager().update(SELECTION_PATH_UNREACHABLE)
        else:
            s = SelectionManager().getSelection(SELECTION_PATH_UNREACHABLE)
            if s:
                s.remove()
                self._movementSelectionUnreachable = None
        if mpLost > 0 or apLost > 0:
            if not self._cursorData:
                cursorSprite = Sprite()
                font = FontManager().getFontInfo("Verdana")
                if font:
                    fontName = font.className
                else:
                    fontName = "Verdana"
                self._tfAP = TextField()
                self._tfAP.selectable = False
                textFormat = TextFormat(fontName, 16, 255, True)
                self._tfAP.defaultTextFormat = textFormat
                self._tfAP.setTextFormat(textFormat)
                self._tfAP.text = "-" + apLost + " " + I18n.getUiText("ui.common.ap")
                if EmbedFontManager().isEmbed(textFormat.font):
                    self._tfAP.embedFonts = True
                self._tfAP.width = self._tfAP.textWidth + 5
                self._tfAP.height = self._tfAP.textHeight
                cursorSprite.addChild(self._tfAP)
                self._tfMP = TextField()
                self._tfMP.selectable = False
                textFormat = TextFormat(fontName, 16, 26112, True)
                self._tfMP.defaultTextFormat = textFormat
                self._tfMP.setTextFormat(textFormat)
                self._tfMP.text = "-" + mpLost + " " + I18n.getUiText("ui.common.mp")
                if EmbedFontManager().isEmbed(textFormat.font):
                    self._tfMP.embedFonts = True
                self._tfMP.width = self._tfMP.textWidth + 5
                self._tfMP.height = self._tfMP.textHeight
                self._tfMP.y = self._tfAP.height
                cursorSprite.addChild(self._tfMP)
                effect = GlowFilter(16777215, 1, 4, 4, 3, 1)
                cursorSprite.filters = [effect]
                self._cursorData = LinkedCursorData()
                self._cursorData.sprite = cursorSprite
                self._cursorData.sprite.cacheAsBitmap = True
                self._cursorData.offset = Point(14, 14)
            if apLost > 0:
                self._tfAP.text = "-" + apLost + " " + I18n.getUiText("ui.common.ap")
                self._tfAP.width = self._tfAP.textWidth + 5
                self._tfAP.visible = True
                self._tfMP.y = self._tfAP.height
            else:
                self._tfAP.visible = False
                self._tfMP.y = 0
            if mpLost > 0:
                self._tfMP.text = "-" + mpLost + " " + I18n.getUiText("ui.common.mp")
                self._tfMP.width = self._tfMP.textWidth + 5
                self._tfMP.visible = True
            else:
                self._tfMP.visible = False
            LinkedCursorSpriteManager().addItem(TAKLED_CURSOR_NAME, self._cursorData, True)
        elif LinkedCursorSpriteManager().getItem(TAKLED_CURSOR_NAME):
            LinkedCursorSpriteManager().removeItem(TAKLED_CURSOR_NAME)
        mp:MapPoint = MapPoint()
        mp.cellId = len(self._cells) > 1 ? int(self._cells[len(self._cells) - 2]) : int(playerInfos.disposition.cellId)
        self._movementSelection.zone = Custom(self._cells)
        SelectionManager().update(SELECTION_PATH, 0, True)
        if len(self._cells) or len(self._cellsTackled):
            cellsToUse = !not len(self._cells) ? self._cells : self._cellsTackled
            if not Dofus().options.getOption("showMovementDistance"):
                orientation = mp.orientationTo(MapPoint.fromCellId(cellsToUse[len(cellsToUse) - 1]))
                if orientation % 2 == 0:
                    orientation += 1
                self._movementTargetSelection.zone = Cross(0, 0, DataMapProvider())
                ZoneClipRenderer(self._movementTargetSelection.renderer).clipNames = ["pathEnd_" + orientation]
            ZoneClipRenderer(self._movementTargetSelection.renderer).currentStrata = !not Atouin().options.getOption("transparentOverlayMode") ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA)
            SelectionManager().update(SELECTION_END_PATH, cellsToUse[len(cellsToUse) - 1], True)

    def updatePath(self) -> None:
        self.drawPath(self._lastCell)

    def removePath(self) -> None:
        s:Selection = SelectionManager().getSelection(SELECTION_PATH)
        if s:
            s.remove()
            self._movementSelection = None
        s = SelectionManager().getSelection(SELECTION_PATH_TACKLED)
        if s:
            s.remove()
            self._movementSelectionTackled = None
        s = SelectionManager().getSelection(SELECTION_PATH_UNREACHABLE)
        if s:
            s.remove()
            self._movementSelectionUnreachable = None
        s = SelectionManager().getSelection(SELECTION_END_PATH)
        if s:
            s.remove()
            self._movementTargetSelection = None
        if LinkedCursorSpriteManager().getItem(TAKLED_CURSOR_NAME):
            LinkedCursorSpriteManager().removeItem(TAKLED_CURSOR_NAME)
        self._lastPath = None
        self._cells = None

    def removeMovementArea(self) -> None:
        s:Selection = SelectionManager().getSelection(SELECTION_MOVEMENT_AREA)
        if s:
            s.remove()
            self._movementAreaSelection = None

    def askMoveTo(self, cell:MapPoint) -> bool:
        gmmrmsg:GameMapMovementRequestMessage = None
        if self._isRequestingMovement:
            return False
        self._isRequestingMovement = True
        if not self._playerEntity:
            logger.warn("The player tried to move before its character was added to the scene. Aborting.")
            return self._isRequestingMovement = False
        if IMovable(self._playerEntity).isMoving:
            return self._isRequestingMovement = False
        if (not self._cells or len(self._cells) == 0) and (not self._cellsTackled or len(self._cellsTackled) == 0):
            return self._isRequestingMovement = False
        path:MovementPath = MovementPath()
        cells:list[int] = self._cells and len(self._cells) ? self._cells : self._cellsTackled
        cells.unshift(self._playerEntity.position.cellId)
        path.fillFromCellIds(cells.slice(0, len(cells) - 1))
        path.start = self._playerEntity.position
        path.end = MapPoint.fromCellId(cells[len(cells) - 1])
        path.path[len(path.path) - 1].orientation = path.path[len(path.path) - 1].step.orientationTo(path.end)
        fightBattleFrame:FightBattleFrame = Kernel().getWorker().getFrame(FightBattleFrame) as FightBattleFrame
        if not fightBattleFrame or not fightBattleFrame.fightIsPaused:
            gmmrmsg = GameMapMovementRequestMessage()
            gmmrmsg.initGameMapMovementRequestMessage(MapMovementAdapter.getServerMovement(path), PlayedCharacterManager().currentMap.mapId)
            ConnectionsHandler.getConnection().send(gmmrmsg)
        else:
            self._isRequestingMovement = False
        self.removePath()
        return True

    def finishTurn(self) -> None:
        gftfmsg:GameFightTurnFinishMessage = GameFightTurnFinishMessage()
        gftfmsg.initGameFightTurnFinishMessage(AFKFightManager().isAfk)
        ConnectionsHandler.getConnection().send(gftfmsg)
        self.removeMovementArea()
        self._finishingTurn = False

    def startRemindTurn(self) -> None:
        if not self._myTurn:
            return
        if self._turnDuration > 0 and Dofus().options.getOption("remindTurn"):
            if self._remindTurnTimeoutId != 0:
                clearTimeout(self._remindTurnTimeoutId)
            self._remindTurnTimeoutId = setTimeout(self.remindTurn, REMIND_TURN_DELAY)

    def remindTurn(self) -> None:
        fightBattleFrame:FightBattleFrame = Kernel().getWorker().getFrame(FightBattleFrame) as FightBattleFrame
        if fightBattleFrame and fightBattleFrame.fightIsPaused:
            clearTimeout(self._remindTurnTimeoutId)
            self._remindTurnTimeoutId = 0
            return
        text:str = I18n.getUiText("ui.fight.inactivity")
        KernelEventsManager().processCallback(ChatHookList.TextInformation, text, ChatFrame.RED_CHANNEL_ID, TimeManager().getTimestamp())
        KernelEventsManager().processCallback(FightHookList.RemindTurn)
        clearTimeout(self._remindTurnTimeoutId)
        self._remindTurnTimeoutId = 0

    def onSecondTick(self) -> None:
        if self._remainingDurationSeconds > 0:
            -- self._remainingDurationSeconds
        else:
            clearInterval(self._intervalTurn)

    def onPropertyChanged(self, e:PropertyChangeEvent) -> None:
        if e.propertyName == "transparentOverlayMode":
            if self._cells and len(self._cells) and SelectionManager().getSelection(SELECTION_END_PATH).visible:
                ZoneClipRenderer(self._movementTargetSelection.renderer).currentStrata = e.propertyValue == True ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA)
                SelectionManager().update(SELECTION_END_PATH, self._cells[len(self._cells) - 1], True)
        elif e.propertyName == "showMovementArea":
            self.drawMovementArea()

    def onUpdateMovementPoints(self, stat:Stat) -> None:
        if stat and stat.entityId == self._currentFighterId and stat.totalValue is not self._lastMP:
            self.drawMovementArea()

