from com.ankama.dofus.enums.ActionIds import ActionIds
from com.ankamagames.atouin.Atouin import Atouin
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.data.map.CellData import CellData
from com.ankamagames.atouin.enums.PlacementStrataEnums import PlacementStrataEnums
from com.ankamagames.atouin.managers.* import *
from com.ankamagames.atouin.messages.AdjacentMapClickMessage import AdjacentMapClickMessage
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.messages.CellOutMessage import CellOutMessage
from com.ankamagames.atouin.messages.CellOverMessage import CellOverMessage
from com.ankamagames.atouin.renderers.* import *
from com.ankamagames.atouin.types.* import *
from com.ankamagames.atouin.utils.CellUtil import CellUtil
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.atouin.utils.IFightZoneRenderer import IFightZoneRenderer
from com.ankamagames.berilia.managers.KernelEventsManager import KernelEventsManager
from com.ankamagames.berilia.managers.LinkedCursorSpriteManager import LinkedCursorSpriteManager
from com.ankamagames.berilia.managers.TooltipManager import TooltipManager
from com.ankamagames.berilia.types.data.LinkedCursorData import LinkedCursorData
from com.ankamagames.berilia.types.tooltip.TooltipPlacer import TooltipPlacer
from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel
from com.ankamagames.dofus.internalDatacenter.items.WeaponWrapper import WeaponWrapper
from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.actions.BannerEmptySlotClickAction import BannerEmptySlotClickAction
from com.ankamagames.dofus.logic.game.fight.actions.TimelineEntityClickAction import TimelineEntityClickAction
from com.ankamagames.dofus.logic.game.fight.actions.TimelineEntityOutAction import TimelineEntityOutAction
from com.ankamagames.dofus.logic.game.fight.actions.TimelineEntityOverAction import TimelineEntityOverAction
from com.ankamagames.dofus.logic.game.fight.frames.Preview.DamagePreview import DamagePreview
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import CurrentPlayedFighterManager
from com.ankamagames.dofus.logic.game.fight.managers.LinkedCellsManager import LinkedCellsManager
from com.ankamagames.dofus.logic.game.fight.managers.MarkedCellsManager import MarkedCellsManager
from com.ankamagames.dofus.logic.game.fight.managers.SpellZoneManager import SpellZoneManager
from com.ankamagames.dofus.logic.game.fight.types.FightSummonPreview import FightSummonPreview
from com.ankamagames.dofus.logic.game.fight.types.FightTeleportationPreview import FightTeleportationPreview
from com.ankamagames.dofus.logic.game.fight.types.MarkInstance import MarkInstance
from com.ankamagames.dofus.logic.game.fight.types.SpellDamage import SpellDamage
from com.ankamagames.dofus.misc.lists.HookList import HookList
from com.ankamagames.dofus.network.enums.ChatActivableChannelsEnum import ChatActivableChannelsEnum
from com.ankamagames.dofus.network.enums.GameActionFightInvisibilityStateEnum import GameActionFightInvisibilityStateEnum
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCastOnTargetRequestMessage import GameActionFightCastOnTargetRequestMessage
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCastRequestMessage import GameActionFightCastRequestMessage
from com.ankamagames.dofus.network.messages.game.chat.ChatClientMultiMessage import ChatClientMultiMessage
from com.ankamagames.dofus.network.types.game.context.GameContextActorInformations import GameContextActorInformations
from com.ankamagames.dofus.network.types.game.context.fight.GameFightCharacterInformations import GameFightCharacterInformations
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import GameFightFighterInformations
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.dofus.types.entities.Glyph import Glyph
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.data.XmlConfig import XmlConfig
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.entities.messages.EntityClickMessage import EntityClickMessage
from com.ankamagames.jerakine.entities.messages.EntityMouseOutMessage import EntityMouseOutMessage
from com.ankamagames.jerakine.entities.messages.EntityMouseOverMessage import EntityMouseOverMessage
from com.ankamagames.jerakine.handlers.messages.mouse.MouseClickMessage import MouseClickMessage
from com.ankamagames.jerakine.handlers.messages.mouse.MouseRightClickMessage import MouseRightClickMessage
from com.ankamagames.jerakine.logger.Log import Log
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.managers.OptionManager import OptionManager
from com.ankamagames.jerakine.map.* import *
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.Color import Color
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.events.PropertyChangeEvent import PropertyChangeEvent
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.zones.Cross import Cross
from com.ankamagames.jerakine.types.zones.Custom import Custom
from com.ankamagames.jerakine.types.zones.IZone import IZone
from com.ankamagames.jerakine.types.zones.Lozenge import Lozenge
from com.ankamagames.jerakine.utils.display.Dofus2Line import Dofus2Line
from com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import EnterFrameDispatcher
from com.ankamagames.jerakine.utils.display.KeyPoll import KeyPoll
from com.ankamagames.jerakine.utils.display.spellZone.SpellShapeEnum import SpellShapeEnum
from com.ankamagames.tiphon.display.TiphonSprite import TiphonSprite
from damageCalculation.damageManagement.EffectOutput import EffectOutput
from damageCalculation.fighterManagement.HaxeFighter import HaxeFighter
from damageCalculation.tools.StatIds import StatIds
from flash.events.TimerEvent import TimerEvent
from flash.geom.Point import Point
from flash.ui.Keyboard import Keyboard
from flash.utils.dict import dict
from flash.utils.getQualifiedClassName import getQualifiedClassName
from haxe.ds._List.ListNode import ListNode
from tools.BreedEnum import BreedEnum
from tools.enumeration.GameActionMarkTypeEnum import GameActionMarkTypeEnum

 class FightSpellCastFrame(Frame):

     SWF_LIB:str = XmlConfig().getEntry:("config.ui.skin").extend("assets_tacticmod.swf")

     FORBIDDEN_CURSOR:Class = FightSpellCastFrame_FORBIDDEN_CURSOR

     logger = Logger(__name__)

     RANGE_COLOR:Color = Color(5533093)

     LOS_COLOR:Color = Color(2241433)

     POSSIBLE_TARGET_CELL_COLOR:Color = Color(3359897)

     PORTAL_COLOR:Color = Color(251623)

     TARGET_CENTER_COLOR:Color = Color(14487842)

     TARGET_COLOR:Color = Color(14487842)

     SELECTION_RANGE:str = "SpellCastRange"

     SELECTION_PORTALS:str = "SpellCastPortals"

     SELECTION_LOS:str = "SpellCastLos"

     SELECTION_TARGET:str = "SpellCastTarget"

     SELECTION_CENTER_TARGET:str = "SELECTION_CENTER_TARGET"

     FORBIDDEN_CURSOR_NAME:str = "SpellCastForbiddenCusror"

     MAX_TOOLTIP:int = 10

     _currentTargetIsTargetable:bool

     _spellLevel:Object

     _spellId:int

     _portalsSelection:Selection

     _targetSelection:Selection

     _targetCenterSelection:Selection

     _currentCell:int = -1

     _cancelTimer:BenchmarkTimer

     _cursorData:LinkedCursorData

     _lastTargetStatus:bool = True

     _isInfiniteTarget:bool

     _usedWrapper

     _targetingThroughPortal:bool

     _clearTargetTimer:BenchmarkTimer

     _spellmaximumRange:int

     _fightTeleportationPreview:FightTeleportationPreview

     _summoningPreview:FightSummonPreview

     _currentCellEntity:AnimatedCharacter

     _fightContextFrame:FightContextFrame

     def __init__(self, spellId:int):
         i:SpellWrapper = None
         weapon:WeaponWrapper = None
         super().__init__()
         self._spellId = spellId
         self._cursorData = LinkedCursorData()
         self._cursorData.sprite = FORBIDDEN_CURSOR()
         self._cursorData.sprite.cacheAsBitmap = True
         self._cursorData.offset = Point(14, 14)
         self._cancelTimer = BenchmarkTimer(50, 0, "FightSpellCastFrame._cancelTimer")
         self._cancelTimer.addEventListener(TimerEvent.TIMER, self.cancelCast)
         if spellId or not PlayedCharacterManager().currentWeapon:
             for each (i in PlayedCharacterManager().spellsInventory)
                 if i.spellId == self._spellId:
                     self._spellLevel = i
         else:
             weapon = PlayedCharacterManager().currentWeapon
                     "effects": weapon.effects,
                     "castTestLos": weapon.castTestLos,
                     "castInLine": weapon.castInLine,
                     "castInDiagonal": weapon.castInDiagonal,
                     "minRange": weapon.minRange,
                     "range": weapon.range,
                     "apCost": weapon.apCost,
                     "needFreeCell": False,
                     "needTakenCell": False,
                     "needFreeTrapCell": False,
                     "name": weapon.name,
                     "playerId": PlayedCharacterManager().id
         self._clearTargetTimer = BenchmarkTimer(50, 1, "FightSpellCastFrame._clearTargetTimer")
         self._clearTargetTimer.addEventListener(TimerEvent.TIMER, self.onClearTarget)

     def isCurrentTargetTargetable(self) -> bool:
         return _currentTargetIsTargetable

     def updateRangeAndTarget(self) -> None:
         castFrame:FightSpellCastFrame = Kernel.getWorker().getFrame(FightSpellCastFrame) as FightSpellCastFrame
         if castFrame:
             castFrame.removeRange()
             castFrame.drawRange()
             castFrame.refreshTarget(True)

     @property
     def priority(self) -> int:
         return Priority.HIGHEST

     @property
     def hasSummoningPreview(self) -> bool:
         return self._summoningPreview and len(self._summoningPreview.previews) > 0

     @property
     def invocationPreview(self) -> list[AnimatedCharacter]:
         if self._summoningPreview:
             return self._summoningPreview.previews
         return null

     @property
     def spellId(self) -> int:
         return self._spellId

     def pushed(self) -> bool:
         actorInfos:GameContextActorInformations = None
         fighterInfos:GameFightFighterInformations = None
         character:AnimatedCharacter = None
         Atouin().options.addEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
         self._fightContextFrame = Kernel.getWorker().getFrame(FightContextFrame) as FightContextFrame
         fef:FightEntitiesFrame = Kernel.getWorker().getFrame(FightEntitiesFrame) as FightEntitiesFrame
         fighters:dict = fef.entities
         for each (actorInfos in fighters)
             fighterInfos = actorInfos as GameFightFighterInformations
             character = DofusEntities.getEntity(fighterInfos.contextualId) as AnimatedCharacter
             if character and fighterInfos.contextualId != CurrentPlayedFighterManager().currentFighterId and fighterInfos.stats.invisibilityState == GameActionFightInvisibilityStateEnum.DETECTED:
                 character.setCanSeeThrough(True)
                 character.setCanWalkThrough(False)
                 character.setCanWalkTo(False)
         self._cancelTimer.reset()
         self._lastTargetStatus = True
         if self._spellId == 0:
             if PlayedCharacterManager().currentWeapon:
                 self._usedWrapper = PlayedCharacterManager().currentWeapon
             else:
                 self._usedWrapper = SpellWrapper.create(0, 1, False, PlayedCharacterManager().id)
         else:
             self._usedWrapper = SpellWrapper.getSpellWrapperById(self._spellId, CurrentPlayedFighterManager().currentFighterId)
         KernelEventsManager().processCallback(HookList.CastSpellMode, self._usedWrapper)
         self.drawRange()
         self.refreshTarget()
         return True

     def process(self, msg:Message) -> bool:
         conmsg:CellOverMessage = None
         comsg:CellOutMessage = None
         cellEntity:IEntity = None
         emomsg:EntityMouseOverMessage = None
         teoa:TimelineEntityOverAction = None
         timelineEntity:IEntity = None
         teouta:TimelineEntityOutAction = None
         outEntity:IEntity = None
         ccmsg:CellClickMessage = None
         ecmsg:EntityClickMessage = None
         teica:TimelineEntityClickAction = None
         switch (True)
          if isinstance(msg, CellOverMessage):
                 conmsg = msg
                 FightContextFrame.currentCell = conmsg.cellId
                 self.refreshTarget()
                 return False
          if isinstance(msg, EntityMouseOutMessage):
                 self.clearTarget()
                 return False
          if isinstance(msg, CellOutMessage):
                 comsg = msg
                 cellEntity = EntitiesManager().getEntityOnCell(comsg.cellId, AnimatedCharacter)
                 self.removeTeleportationPreview()
                 self.removeSummoningPreview()
                 self.clearTarget()
                 return False
          if isinstance(msg, EntityMouseOverMessage):
                 emomsg = msg
                 FightContextFrame.currentCell = emomsg.entity.position.cellId
                 self.refreshTarget()
                 return False
          if isinstance(msg, TimelineEntityOverAction):
                 teoa = msg
                 timelineEntity = DofusEntities.getEntity(teoa.targetId)
                 if timelineEntity and timelineEntity.position and timelineEntity.position.cellId > -1:
                     FightContextFrame.currentCell = timelineEntity.position.cellId
                     self.refreshTarget()
                 return False
          if isinstance(msg, TimelineEntityOutAction):
                 teouta = msg
                 outEntity = DofusEntities.getEntity(teouta.targetId)
                 self.removeTeleportationPreview()
                 self.removeSummoningPreview()
                 return False
          if isinstance(msg, CellClickMessage):
                 ccmsg = msg
                 self.castSpell(ccmsg.cellId)
                 return True
          if isinstance(msg, EntityClickMessage):
                 ecmsg = msg
                 if self._summoningPreview and self._summoningPreview.isPreview(ecmsg.entity.id) or self._fightTeleportationPreview and self._fightTeleportationPreview.isPreview(ecmsg.entity.id):
                     self.castSpell(ecmsg.entity.position.cellId)
                 else:
                     self.castSpell(ecmsg.entity.position.cellId, ecmsg.entity.id)
                 return True
          if isinstance(msg, TimelineEntityClickAction):
                 teica = msg
                 self.castSpell(0, teica.fighterId, True)
                 return True
          if isinstance(msg, AdjacentMapClickMessage):
          if isinstance(msg, MouseRightClickMessage):
                 self.cancelCast()
                 return True
          if isinstance(msg, BannerEmptySlotClickAction):
                 self.cancelCast()
                 return True
          if isinstance(msg, MouseClickMessage):
                 if (not KeyPoll().isDown(Keyboard.ALTERNATE) and !(msg.target is GraphicCell and self.isValidCellGraphicCell((msg
                     self._cancelTimer.start()
                 return False
          else:
                 return False

     def pulled(self) -> bool:
         fef:FightEntitiesFrame = None
         fighters:dict = None
         actorInfos:GameContextActorInformations = None
         fighterInfos:GameFightFighterInformations = None
         character:AnimatedCharacter = None
         Atouin().options.removeEventListener(PropertyChangeEvent.PROPERTY_CHANGED, self.onPropertyChanged)
         fbf:FightBattleFrame = Kernel.getWorker().getFrame(FightBattleFrame) as FightBattleFrame
         if fbf:
             fef = Kernel.getWorker().getFrame(FightEntitiesFrame) as FightEntitiesFrame
             fighters = fef.entities
             for each (actorInfos in fighters)
                 fighterInfos = actorInfos as GameFightFighterInformations
                 character = DofusEntities.getEntity(actorInfos.contextualId) as AnimatedCharacter
                 if character and actorInfos.contextualId != CurrentPlayedFighterManager().currentFighterId and fighterInfos.stats.invisibilityState == GameActionFightInvisibilityStateEnum.VISIBLE:
                     character.setCanSeeThrough(False)
                     character.setCanWalkThrough(False)
                     character.setCanWalkTo(False)
         self._clearTargetTimer.stop()
         self._clearTargetTimer.removeEventListener(TimerEvent.TIMER, self.onClearTarget)
         self._cancelTimer.stop()
         self._cancelTimer.removeEventListener(TimerEvent.TIMER, self.cancelCast)
         self.hideTargetsTooltips()
         self.removeRange()
         self.removeTarget()
         self.removeSummoningPreview()
         LinkedCursorSpriteManager().removeItem(FORBIDDEN_CURSOR_NAME)
         self.removeTeleportationPreview(True)
         try:
             KernelEventsManager().processCallback(HookList.CancelCastSpell, SpellWrapper.getSpellWrapperById(self._spellId, CurrentPlayedFighterManager().currentFighterId))
         catch (e:Error)
         return True

     def entityMovement(self, pEntityId:float) -> None:
         if self._currentCellEntity and self._currentCellEntity.id == pEntityId:
             self.removeSummoningPreview()
             if self._fightTeleportationPreview:
                 self.removeTeleportationPreview()
         elif self._fightTeleportationPreview and self._fightTeleportationPreview.getEntitiesIds().find(pEntityId) != -1:
             self.removeTeleportationPreview()

     def refreshTarget(self, force:bool = False) -> None:
         currentFighterId:float = None
         entityInfos:GameFightFighterInformations = None
         renderer:IFightZoneRenderer = None
         ignoreMaxSize:bool = False
         spellShape:int = 0
         entityInfo:GameContextActorInformations = None
         cellId:int = 0
         spellZone:IZone = None
         updateStrata:bool = False
         if self._clearTargetTimer.running:
             self._clearTargetTimer.reset()
         target:int = FightContextFrame.currentCell
         if target == -1:
             return
         self._targetingThroughPortal = False
         newTarget:int = -1
         if SelectionManager().isInside(target, SELECTION_PORTALS) and SelectionManager().isInside(target, SELECTION_LOS) and self._spellId != 0:
             newTarget = self.getTargetThroughPortal(target, True)
             if newTarget != target:
                 self._targetingThroughPortal = True
                 target = newTarget
         self.removeSummoningPreview()
         self.removeTeleportationPreview()
         if not force and (self._currentCell == target and self._currentCell != newTarget):
             if self._targetSelection and self.isValidCell(target):
                 self.showTargetsTooltips()
             return
         self._currentCell = target
         entitiesOnCell:list = EntitiesManager().getEntitiesOnCell(self._currentCell, AnimatedCharacter)
         self._currentCellEntity = len(entitiesOnCell) > 0 ? self.getParentEntity(entitiesOnCell[0]) as AnimatedCharacter : null
         fightTurnFrame:FightTurnFrame = Kernel.getWorker().getFrame(FightTurnFrame) as FightTurnFrame
         if not fightTurnFrame:
             return
         myTurn:bool = fightTurnFrame.myTurn
         _currentTargetIsTargetable = self.isValidCell(target)
         if _currentTargetIsTargetable:
             if not self._targetSelection:
                 self._targetSelection = Selection()
                 self._targetSelection.renderer = self.createZoneRenderer(TARGET_COLOR)
                 self._targetSelection.color = TARGET_COLOR
                 self._targetCenterSelection = Selection()
                 self._targetCenterSelection.renderer = self.createZoneRenderer(TARGET_CENTER_COLOR, !not Atouin().options.getOption("transparentOverlayMode") ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA))
                 self._targetCenterSelection.color = TARGET_CENTER_COLOR
                 ignoreMaxSize = True
                 spellShape = self.getSpellShape()
                 if spellShape == SpellShapeEnum.l:
                     ignoreMaxSize = False
                 self._targetCenterSelection.zone = Cross(0, 0, DataMapProvider())
                 SelectionManager().addSelection(self._targetCenterSelection, SELECTION_CENTER_TARGET)
                 SelectionManager().addSelection(self._targetSelection, SELECTION_TARGET)
             if not self._targetSelection.zone or self._targetSelection.zone is Custom:
                 entityInfo = FightEntitiesFrame.getCurrentInstance().getEntityInfos(self._spellLevel.playerId)
                 if entityInfo:
                     cellId = entityInfo.disposition.cellId
                     spellZone = SpellZoneManager().getSpellZone(self._spellLevel, True, ignoreMaxSize, target, cellId)
                     self._spellmaximumRange = spellZone.radius
                     self._targetSelection.zone = spellZone
             currentFighterId = CurrentPlayedFighterManager().currentFighterId
             entityInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(currentFighterId) as GameFightFighterInformations
             if entityInfos:
                 if self._targetingThroughPortal:
                     self._targetSelection.zone.direction = MapPoint(MapPoint.fromCellId(entityInfos.disposition.cellId)).advancedOrientationTo(MapPoint.fromCellId(FightContextFrame.currentCell), False)
                 else:
                     self._targetSelection.zone.direction = MapPoint(MapPoint.fromCellId(entityInfos.disposition.cellId)).advancedOrientationTo(MapPoint.fromCellId(target), False)
             renderer = self._targetSelection.renderer as IFightZoneRenderer
             if Atouin().options.getOption("transparentOverlayMode") and self._spellmaximumRange != 63:
                 renderer.currentStrata = PlacementStrataEnums.STRATA_NO_Z_ORDER
                 SelectionManager().update(SELECTION_TARGET, target, True)
                 SelectionManager().update(SELECTION_CENTER_TARGET, target, True)
             else:
                 if renderer.currentStrata == PlacementStrataEnums.STRATA_NO_Z_ORDER:
                     renderer.currentStrata = PlacementStrataEnums.STRATA_AREA
                     updateStrata = True
                 SelectionManager().update(SELECTION_TARGET, target, updateStrata)
                 SelectionManager().update(SELECTION_CENTER_TARGET, target, updateStrata)
             if myTurn:
                 LinkedCursorSpriteManager().removeItem(FORBIDDEN_CURSOR_NAME)
                 self._lastTargetStatus = True
             else:
                 if self._lastTargetStatus:
                     LinkedCursorSpriteManager().addItem(FORBIDDEN_CURSOR_NAME, self._cursorData, True)
                 self._lastTargetStatus = False
             self.showTargetsTooltips()
         else:
             if self._lastTargetStatus:
                 LinkedCursorSpriteManager().addItem(FORBIDDEN_CURSOR_NAME, self._cursorData, True)
             self.removeTarget()
             self._lastTargetStatus = False
             self.hideTargetsTooltips()

     def isTeleportationPreviewEntity(self, pEntityId:float) -> bool:
         return self._fightTeleportationPreview and self._fightTeleportationPreview.isPreview(pEntityId)

     def isSummoningPreviewEntity(self, pEntityId:float) -> bool:
         return self._summoningPreview and self._summoningPreview.isPreview(pEntityId)

     def getSummonPreview(self, pEntityId:float) -> AnimatedCharacter:
         if self._summoningPreview:
             return self._summoningPreview.getSummonPreview(pEntityId)
         return null

     def drawRange(self) -> None:
         shapePlus:Cross = None
         selectionCellId:int = 0
         noLosRangeCell:list[int] = None
         losRangeCell:list[int] = None
         num:int = 0
         i:int = 0
         cellId:int = 0
         cAfterPortal:int = 0
         exitPortal:int = 0
         c:int = 0
         entry:MarkPortal:MarkInstance = None
         teamPortals:list[MapPoint] = None
         portalsCellIds:list[int] = None
         lastPortalMp:MapPoint = None
         newTargetMp:MapPoint = None
         cellsFromLine:list = None
         mp:MapPoint = None
         cellFromLine:Point = None
         cellsWithLosOk:list[int] = None
         if self._spellLevel == null:
             return
         currentFighterId:float = CurrentPlayedFighterManager().currentFighterId
         entityInfos:GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(currentFighterId) as GameFightFighterInformations
         origin:int = entityInfos.disposition.cellId
         playerStats:EntityStats = CurrentPlayedFighterManager().getStats()
         range:int = self._spellLevel.range
         minRange:int = self._spellLevel.minRange
         spellShape:int = self.getSpellShape()
         castInLine:bool = self._spellLevel.castInLine or spellShape == SpellShapeEnum.l
         mpWithPortals:list[MapPoint] = MarkedCellsManager().getMarksMapPoint(GameActionMarkTypeEnum.PORTAL)
         if not castInLine and not self._spellLevel.castInDiagonal and not self._spellLevel.castTestLos and range == 63:
             self._isInfiniteTarget = True
             if mpWithPortals == null or len(mpWithPortals) < 2:
                 return
         else:
             self._isInfiniteTarget = False
         if self._spellLevel["rangeCanBeBoosted"]:
             range += playerStats.getStatTotalValue(StatIds.RANGE) - playerStats.getStatAdditionalValue(StatIds.RANGE)
         if range < minRange:
             range = minRange
         range = min(range, AtouinConstants.MAP_WIDTH * AtouinConstants.MAP_HEIGHT)
         if range < 0:
             range = 0
         rangeSelection:Selection = Selection()
         rangeSelection.renderer = self.createZoneRenderer(RANGE_COLOR, PlacementStrataEnums.STRATA_AREA)
         rangeSelection.color = RANGE_COLOR
         rangeSelection.alpha = True
         if castInLine and self._spellLevel.castInDiagonal:
             shapePlus = Cross(minRange, range, DataMapProvider())
             shapePlus.allDirections = True
             rangeSelection.zone = shapePlus
         elif castInLine:
             rangeSelection.zone = Cross(minRange, range, DataMapProvider())
         elif self._spellLevel.castInDiagonal:
             shapePlus = Cross(minRange, range, DataMapProvider())
             shapePlus.diagonal = True
             rangeSelection.zone = shapePlus
         else:
             rangeSelection.zone = Lozenge(minRange, range, DataMapProvider())
         untargetableCells:list[int] = list[int]()
         losSelection:Selection = Selection()
         if not self._isInfiniteTarget:
             losSelection.renderer = self.createZoneRenderer(LOS_COLOR, PlacementStrataEnums.STRATA_AREA)
             losSelection.color = LOS_COLOR
         allCells:list[int] = rangeSelection.zone.getCells(origin)
         if not self._spellLevel.castTestLos:
             losSelection.zone = Custom(allCells)
         else:
             losSelection.zone = Custom(LosDetector.getCell(DataMapProvider(), allCells, MapPoint.fromCellId(origin)))
             rangeSelection.renderer = self.createZoneRenderer(POSSIBLE_TARGET_CELL_COLOR, PlacementStrataEnums.STRATA_AREA)
             noLosRangeCell = rangeSelection.zone.getCells(origin)
             losRangeCell = losSelection.zone.getCells(origin)
             num = len(noLosRangeCell)
             for (i = 0 i < num i += 1)
                 cellId = noLosRangeCell[i]
                 if losRangeCell.find(cellId) == -1:
                     untargetableCells.append(cellId)
         portalUsableCells:list[int] = list[int]()
         cells:list[int] = list[int]()
         if mpWithPortals and len(mpWithPortals) >= 2:
             for each (c in losSelection.zone.getCells(origin))
                 cAfterPortal = self.getTargetThroughPortal(c)
                 if cAfterPortal != c:
                     self._targetingThroughPortal = True
                     if self.isValidCell(cAfterPortal, True):
                         if self._spellLevel.castTestLos:
                             entry:MarkPortal = MarkedCellsManager().getMarkAtCellId(c, GameActionMarkTypeEnum.PORTAL)
                             teamPortals = MarkedCellsManager().getMarksMapPoint(GameActionMarkTypeEnum.PORTAL, entry:MarkPortal.teamId)
                             portalsCellIds = LinkedCellsManager().getLinks(MapPoint.fromCellId(c), teamPortals)
                             exitPortal = portalsCellIds.pop()
                             lastPortalMp = MapPoint.fromCellId(exitPortal)
                             newTargetMp = MapPoint.fromCellId(cAfterPortal)
                             cellsFromLine = Dofus2Line.getLine(lastPortalMp.cellId, newTargetMp.cellId)
                             for each (cellFromLine in cellsFromLine)
                                 mp = MapPoint.fromCoords(cellFromLine.x, cellFromLine.y)
                                 cells.append(mp.cellId)
                             cellsWithLosOk = LosDetector.getCell(DataMapProvider(), cells, lastPortalMp)
                             if cellsWithLosOk.find(cAfterPortal) > -1:
                                 portalUsableCells.append(c)
                             else:
                                 untargetableCells.append(c)
                         else:
                             portalUsableCells.append(c)
                     else:
                         untargetableCells.append(c)
                     self._targetingThroughPortal = False
         losCells:list[int] = list[int]()
         losSelectionCells:list[int] = losSelection.zone.getCells(origin)
         for each (selectionCellId in losSelectionCells)
             if portalUsableCells.find(selectionCellId) != -1:
                 losCells.append(selectionCellId)
             elif self._usedWrapper is SpellWrapper and self._usedWrapper.spellLevelInfos and (self._usedWrapper.spellLevelInfos.needFreeCell and self.cellHasEntity(selectionCellId) or self._usedWrapper.spellLevelInfos.needFreeTrapCell and MarkedCellsManager().cellHasTrap(selectionCellId)):
                 untargetableCells.append(selectionCellId)
             elif untargetableCells.find(selectionCellId) == -1:
                 losCells.append(selectionCellId)
         losSelection.zone = Custom(losCells)
         SelectionManager().addSelection(losSelection, SELECTION_LOS, origin)
         if len(untargetableCells) > 0:
             rangeSelection.zone = Custom(untargetableCells)
             SelectionManager().addSelection(rangeSelection, SELECTION_RANGE, origin)
         else:
             rangeSelection.zone = Custom(list[int]())
             SelectionManager().addSelection(rangeSelection, SELECTION_RANGE, origin)
         if len(portalUsableCells) > 0:
             self._portalsSelection = Selection()
             self._portalsSelection.renderer = self.createZoneRenderer(PORTAL_COLOR, PlacementStrataEnums.STRATA_AREA)
             self._portalsSelection.color = PORTAL_COLOR
             self._portalsSelection.alpha = True
             self._portalsSelection.zone = Custom(portalUsableCells)
             SelectionManager().addSelection(self._portalsSelection, SELECTION_PORTALS, origin)

     def removeTeleportationPreview(self, destroy:bool = False) -> None:
         if self._fightTeleportationPreview:
             self._fightTeleportationPreview.remove(destroy)
             if destroy:
                 self._fightTeleportationPreview = None

     def removeSummoningPreview(self) -> None:
         if self._summoningPreview:
             self._summoningPreview.remove()

     def getParentEntity(self, pEntity:TiphonSprite) -> TiphonSprite:
         parentEntity:TiphonSprite = None
         parent:TiphonSprite = pEntity.parentSprite
         while (parent)
             parentEntity = parent
             parent = parent.parentSprite
         return not parentEntity ? pEntity : parentEntity

     def showTargetsTooltips(self) -> None:
         paramsToShow:list[Object] = None
         movedFighters:list[HaxeFighter] = None
         summonedFighters:list[HaxeFighter] = None
         limitedParams:list[Object] = None
         result:Object = None
         entityId:float = None
         hide:bool = False
         params:Object = None
         movementPreview:AnimatedCharacter = None
         entId:float = None
         entity:AnimatedCharacter = None
         entitiesIds:list[Number] = self._fightContextFrame.entitiesFrame.getEntitiesIdsList()
         showDamages:bool = self._spellLevel and OptionManager.getOptionManager("dofus").getOption("showDamagesPreview") == True and FightSpellCastFrame.isCurrentTargetTargetable()
         showMove:bool = self._spellLevel and OptionManager.getOptionManager("dofus").getOption("showMovePreview") == True and FightSpellCastFrame.isCurrentTargetTargetable()
         if showDamages or showMove:
             result = self.damagePreview()
             paramsToShow = result.damages
             movedFighters = result.movements
             summonedFighters = result.summoned
         self._fightContextFrame.removeSpellTargetsTooltips()
         if showMove and movedFighters:
             self.removeSummoningPreview()
             if len(summonedFighters) > 0:
                 self._summoningPreview = FightSummonPreview(summonedFighters)
                 self._summoningPreview.show()
             self.removeTeleportationPreview()
             if len(movedFighters) > 0:
                 if not self._fightTeleportationPreview:
                     self._fightTeleportationPreview = FightTeleportationPreview(movedFighters)
                 else:
                     self._fightTeleportationPreview.init(movedFighters)
                 self._fightTeleportationPreview.show(self)
         if paramsToShow:
             limitedParams = paramsToShow.slice(0, MAX_TOOLTIP)
             for each (entityId in entitiesIds)
                 hide = True
                 if limitedParams:
                     for each (params in limitedParams)
                         if params.fighterId == entityId:
                             if self._fightTeleportationPreview != null:
                                 movementPreview = self._fightTeleportationPreview.getPreview(entityId)
                                 if movementPreview != null:
                                     params.previewEntity = movementPreview
                             TooltipPlacer.waitBeforeOrder("tooltip_tooltipOverEntity_" + entityId)
                             hide = False
                 if hide:
                     TooltipManager.hide("tooltip_tooltipOverEntity_" + entityId)
         else:
             for each (entId in entitiesIds)
                 TooltipManager.hide("tooltip_tooltipOverEntity_" + entId)
         if showDamages and limitedParams and len(limitedParams) > 0:
             EnterFrameDispatcher.worker.addForeachTreatment(self, self.displayEntityTooltipTreatment, [self._spellLevel, self._currentCell], limitedParams)
         else:
             entity = EntitiesManager().getEntityOnCell(self._currentCell, AnimatedCharacter) as AnimatedCharacter
             if entity != null:
                 self._fightContextFrame.displayEntityTooltip(entity.id, null, False, self._currentCell)

     def displayEntityTooltipTreatment(self, params:Object, spellLevel:int, currentCell:int) -> None:
         self._fightContextFrame.displayEntityTooltip(params.fighterId, spellLevel, True, currentCell, params)

     def damagePreview(self) -> Object:
         currentFighter:HaxeFighter = None
         infos:GameFightCharacterInformations = None
         spellDamage:SpellDamage = None
         cursor:ListNode = None
         params:Object = None
         currentEffect:EffectOutput = None
         affectedFighters:list = DamagePreview.computePreview(self._fightContextFrame, self._spellLevel, CurrentPlayedFighterManager().currentFighterId, self._currentCell)
         movedFighters:list[HaxeFighter] = list[HaxeFighter]()
         summonedFighters:list[HaxeFighter] = list[HaxeFighter]()
         paramsToShow:list[Object] = list[Object]()
         currentCharacterIsXelor:bool = False
         entityInfos:GameContextActorInformations = self._fightContextFrame.entitiesFrame.getEntityInfos(CurrentPlayedFighterManager().currentFighterId)
         if isinstance(entityInfos, GameFightCharacterInformations):
             infos = GameFightCharacterInformations(entityInfos)
             if infos != null and infos.breed == BreedEnum.Xelor:
                 currentCharacterIsXelor = True
         for each (currentFighter in affectedFighters)
             spellDamage = SpellDamage()
             cursor = currentFighter.totalEffects.h
             while (cursor != null)
                 currentEffect = cursor.item as EffectOutput
                 if currentEffect.damageRange != null:
                     if currentEffect.shield != null and not currentEffect.shield.isZero():
                         spellDamage.addDamageRange(currentEffect.computeShieldDamage())
                     spellDamage.addDamageRange(currentEffect.computeLifeDamage())
                     if currentEffect.unknown:
                         spellDamage.unknownDamage = True
                 elif currentEffect.movement != null or currentEffect.isPulled or currentEffect.isPushed:
                     if movedFighters.find(currentFighter) == -1:
                         movedFighters.append(currentFighter)
                     if currentEffect.movement != null and currentEffect.movement.swappedWith != null and currentCharacterIsXelor:
                         spellDamage.telefrag = True
                 elif currentEffect.summon != null:
                     summonedFighters.append(currentFighter)
                 cursor = cursor.next
             if spellDamage.hasDamage():
                 spellDamage.updateDamage()
                 params.spellDamage = spellDamage
             params.fighterId = currentFighter.id
             paramsToShow.append(params)
                 "damages": paramsToShow,
                 "movements": movedFighters,
                 "summoned": summonedFighters

     def hideTargetsTooltips(self) -> None:
         entityId:float = None
         ac:AnimatedCharacter = None
         if not self._fightContextFrame or not self._fightContextFrame.entitiesFrame:
             return
         entitiesId:list[Number] = self._fightContextFrame.entitiesFrame.getEntitiesIdsList()
         overEntity:IEntity = EntitiesManager().getEntityOnCell(FightContextFrame.currentCell, AnimatedCharacter)
         if overEntity:
             ac = overEntity as AnimatedCharacter
             if ac and ac.parentSprite and ac.parentSprite.carriedEntity == ac:
                 overEntity = ac.parentSprite as AnimatedCharacter
         for each (entityId in entitiesId)
             if not self._fightContextFrame.showPermanentTooltips or self._fightContextFrame.showPermanentTooltips and self._fightContextFrame.battleFrame.targetedEntities.find(entityId) == -1:
                 TooltipManager.hide("tooltipOverEntity_" + entityId)
         if self._fightContextFrame.showPermanentTooltips and self._fightContextFrame.battleFrame and self._fightContextFrame.battleFrame.targetedEntities and self._fightContextFralen(me.battleFrame.targetedEntities) > 0:
             for each (entityId in self._fightContextFrame.battleFrame.targetedEntities)
                 if not overEntity or entityId != overEntity.id:
                     self._fightContextFrame.displayEntityTooltip(entityId)
         if overEntity:
             self._fightContextFrame.displayEntityTooltip(overEntity.id)

     def clearTarget(self) -> None:
         if not self._clearTargetTimer.running:
             self._clearTargetTimer.start()

     def onClearTarget(self, event:TimerEvent) -> None:
         self.refreshTarget()

     def getTargetThroughPortal(self, target:int, drawLinks:bool = False) -> int:
         targetPortal:MapPoint = None
         portalMark:MarkInstance = None
         portalp:MapPoint = None
         effect:EffectInstance = None
         newTargetPoint:MapPoint = None
         entry:Vector:list[int] = None
         exitVector:list[int] = None
         if self._spellLevel and self._spellLevel.effects:
             for each (effect in self._spellLevel.effects)
                 if effect.effectId == ActionIds.ACTION_FIGHT_DISABLE_PORTAL:
                     return target
         currentFighterId:float = CurrentPlayedFighterManager().currentFighterId
         entityInfos:GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(currentFighterId) as GameFightFighterInformations
         if not entityInfos:
             return target
         markedCellsManager:MarkedCellsManager = MarkedCellsManager()
         mpWithPortals:list[MapPoint] = markedCellsManager.getMarksMapPoint(GameActionMarkTypeEnum.PORTAL)
         if not mpWithPortals or len(mpWithPortals) < 2:
             return target
         for each (portalp in mpWithPortals)
             portalMark = markedCellsManager.getMarkAtCellId(portalp.cellId, GameActionMarkTypeEnum.PORTAL)
             if portalMark and portalMark.active:
                 if portalp.cellId == target:
                     targetPortal = portalp
         if not targetPortal:
             return target
         mpWithPortals = markedCellsManager.getMarksMapPoint(GameActionMarkTypeEnum.PORTAL, portalMark.teamId)
         portalsCellIds:list[int] = LinkedCellsManager().getLinks(targetPortal, mpWithPortals)
         exitPoint:MapPoint = MapPoint.fromCellId(portalsCellIds.pop())
         fighterPoint:MapPoint = MapPoint.fromCellId(entityInfos.disposition.cellId)
         if not fighterPoint:
             return target
         symmetricalTargetX:int = targetPortal.x - fighterPoint.x + exitPoint.x
         symmetricalTargetY:int = targetPortal.y - fighterPoint.y + exitPoint.y
         if not MapPoint.isInMap(symmetricalTargetX, symmetricalTargetY):
             return AtouinConstants.MAP_CELLS_COUNT + 1
         newTargetPoint = MapPoint.fromCoords(symmetricalTargetX, symmetricalTargetY)
         if drawLinks:
             entry:Vector = list[int]()
             entry:Vector.append(fighterPoint.cellId)
             entry:Vector.append(targetPortal.cellId)
             LinkedCellsManager().drawLinks("spellEntry:Link", entry:Vector, 10, TARGET_COLOR.color, 1)
             if newTargetPoint.cellId < AtouinConstants.MAP_CELLS_COUNT:
                 exitVector = list[int]()
                 exitVector.append(exitPoint.cellId)
                 exitVector.append(newTargetPoint.cellId)
                 LinkedCellsManager().drawLinks("spellExitLink", exitVector, 6, TARGET_COLOR.color, 1)
         return newTargetPoint.cellId

     def checkSpellCostAndPlayerAp(self) -> int:
         spell:SpellWrapper = None
         for each (spell in PlayedCharacterManager().spellsInventory)
             if spell.spellId == self._spellLevel.spellId and spell.apCost != self._spellLevel.apCost:
                 self._spellLevel.apCost = spell.apCost
         return CurrentPlayedFighterManager().getStats().getStatTotalValue(StatIds.ACTION_POINTS)

     def castSpell(self, cell:int, targetId:float = 0, forceCheckForRange:bool = False) -> None:
         entity:IEntity = None
         text:str = None
         targetName = None
         fighter:GameFightFighterInformations = None
         spellName = None
         ccmmsg:ChatClientMultiMessage = None
         cellEntity:IEntity = None
         gafcotrmsg:GameActionFightCastOnTargetRequestMessage = None
         gafcrmsg:GameActionFightCastRequestMessage = None
         fightTurnFrame:FightTurnFrame = Kernel.getWorker().getFrame(FightTurnFrame) as FightTurnFrame
         if not fightTurnFrame:
             return
         apCurrent:int = self.checkSpellCostAndPlayerAp()
         if apCurrent < self._spellLevel.apCost:
             return
         if KeyPoll().isDown(Keyboard.ALTERNATE):
             if cell == 0 and targetId != 0:
                 entity = DofusEntities.getEntity(targetId)
                 if entity and entity.position:
                     cell = entity.position.cellId
             if targetId == 0 and cell > 0:
                 cellEntity = EntitiesManager().getEntityOnCell(cell, AnimatedCharacter)
                 if cellEntity:
                     targetId = cellEntity.id
             if targetId != 0 and not entity:
                 fighter = FightEntitiesFrame.getCurrentInstance().getEntityInfos(targetId) as GameFightFighterInformations
             if fighter and fighter.disposition.cellId:
             else:
             if self._spellId == 0:
                 spellName = self._spellLevel.name
             else:
             if SelectionManager().isInside(cell, SELECTION_RANGE):
                 text = I18n.getUiText("ui.fightAutomsg.targetcast.noLineOfSight", [spellName, targetName])
             elif not SelectionManager().isInside(cell, SELECTION_LOS):
                 text = I18n.getUiText("ui.fightAutomsg.targetcast.outsideRange", [spellName, targetName])
             else:
                 text = I18n.getUiText("ui.fightAutomsg.targetcast.available", [spellName, targetName])
             ccmmsg = ChatClientMultiMessage()
             ccmmsg.initChatClientMultiMessage(text, ChatActivableChannelsEnum.CHANNEL_TEAM)
             ConnectionsHandler.getConnection().send(ccmmsg)
             return
         if forceCheckForRange and self._spellLevel.maximalRange < 63:
             if cell == 0 and targetId != 0:
                 entity = DofusEntities.getEntity(targetId)
                 if entity and entity.position:
                     cell = entity.position.cellId
             if SelectionManager().isInside(cell, SELECTION_RANGE) or not SelectionManager().isInside(cell, SELECTION_LOS):
                 return
         if not fightTurnFrame.myTurn:
             return
         fightBattleFrame:FightBattleFrame = Kernel.getWorker().getFrame(FightBattleFrame) as FightBattleFrame
         if fightBattleFrame and fightBattleFrame.fightIsPaused:
             self.cancelCast()
             return
         if targetId != 0 and not FightEntitiesFrame.getCurrentInstance().entityIsIllusion(targetId) and !(self._fightTeleportationPreview and self._fightTeleportationPreview.isPreview(targetId)) and CurrentPlayedFighterManager().canCastThisSpell(self._spellId, self._spellLevel.spellLevel, targetId):
             gafcotrmsg = GameActionFightCastOnTargetRequestMessage()
             gafcotrmsg.initGameActionFightCastOnTargetRequestMessage(self._spellId, targetId)
             ConnectionsHandler.getConnection().send(gafcotrmsg)
         elif self.isValidCell(cell):
             self.removeSummoningPreview()
             self.removeTeleportationPreview(True)
             gafcrmsg = GameActionFightCastRequestMessage()
             gafcrmsg.initGameActionFightCastRequestMessage(self._spellId, cell)
             ConnectionsHandler.getConnection().send(gafcrmsg)
         self.cancelCast()

     def cancelCast(self, ...args) -> None:
         self.removeSummoningPreview()
         self.removeTeleportationPreview(True)
         self._cancelTimer.reset()
         Kernel.getWorker().removeFrame(self)

     def removeRange(self) -> None:
         s:Selection = SelectionManager().getSelection(SELECTION_RANGE)
         if s:
             s.remove()
         los:Selection = SelectionManager().getSelection(SELECTION_LOS)
         if los:
             los.remove()
         ps:Selection = SelectionManager().getSelection(SELECTION_PORTALS)
         if ps:
             ps.remove()
             self._portalsSelection = None
         self._isInfiniteTarget = False

     def removeTarget(self) -> None:
         s:Selection = SelectionManager().getSelection(SELECTION_TARGET)
         if s:
             s.remove()
         s = SelectionManager().getSelection(SELECTION_CENTER_TARGET)
         if s:
             s.remove()

     def cellHasEntity(self, cellId:int) -> bool:
         isPreviewedEntity:bool = False
         entity:IEntity = None
         entities:list = EntitiesManager().getEntitiesOnCell(cellId, AnimatedCharacter)
         if entities == null or len(entities) <= 0:
             return False
         isSummoningPreview:bool = self.hasSummoningPreview
         isTeleportationPreview = self._fightTeleportationPreview is not null
         entityId:float = Number.None
         for each (entity in entities)
             entityId = entity.id
             isPreviewedEntity = False
             if isSummoningPreview:
                 if self._summoningPreview.isPreview(entityId):
                     isPreviewedEntity = True
             if not isPreviewedEntity and isTeleportationPreview:
                 if self._fightTeleportationPreview.isPreview(entityId):
                     isPreviewedEntity = True
             if not isPreviewedEntity:
                 return True
         return False

     def isValidCell(self, cell:int, ignorePortal:bool = False) -> bool:
         spellLevel:SpellLevel = None
         entities:list = None
         entity:IEntity = None
         isGlyph = False
         valid:bool = False
         if not CellUtil.isValidCellIndex(cell):
             return False
         cellData:CellData = MapDisplayManager().getDataMapContainer().dataMap.cells[cell]
         if not cellData or cellData.farmCell:
             return False
         if self._isInfiniteTarget:
             return True
         if self._spellId and self._spellLevel:
             spellLevel = self._spellLevel.spellLevelInfos
             entities = EntitiesManager().getEntitiesOnCell(cell)
             for each (entity in entities)
                 if !(self.isTeleportationPreviewEntity(entity.id) or self.isSummoningPreviewEntity(entity.id)):
                     if not CurrentPlayedFighterManager().canCastThisSpell(self._spellLevel.spellId, self._spellLevel.spellLevel, entity.id):
                         return False
                     isGlyph = entity is Glyph
                     if spellLevel.needFreeTrapCell and isGlyph and entity.glyphType == GameActionMarkTypeEnum.TRAP:
                         return False
                     if self._spellLevel.needFreeCell and not isGlyph:
                         return False
         if self._targetingThroughPortal and not ignorePortal:
             valid = self.isValidCell(self.getTargetThroughPortal(cell), True)
             if not valid:
                 return False
         if self._targetingThroughPortal:
             if cellData.nonWalkableDuringFight:
                 return False
             return cellData.mov
         return SelectionManager().isInside(cell, SELECTION_LOS)

     def getSpellShape(self) -> int:
         spellShape:int = 0
         spellEffect:EffectInstance = None
         for each (spellEffect in self._spellLevel.effects)
             if spellEffect.zoneShape != 0 and (spellEffect.zoneSize > 0 or spellEffect.zoneSize == 0 and (spellEffect.zoneShape == SpellShapeEnum.P or spellEffect.zoneMinSize < 0)):
                 spellShape = spellEffect.zoneShape
         return spellShape

     def createZoneRenderer(self, color:Color, strata:int = 90) -> IFightZoneRenderer:
         renderer:IFightZoneRenderer = None
         switch (color)
          if None  == TARGET_CENTER_COLOR:
                 renderer = ZoneClipRenderer(strata, SWF_LIB, ["cellActive"], -1, False, False)
          else:
                 renderer = ZoneDARenderer(PlacementStrataEnums.STRATA_AREA, 1, True)
         renderer.showFarmCell = False
         return renderer

     def onPropertyChanged(self, e:PropertyChangeEvent) -> None:
         if self._targetCenterSelection and self._targetCenterSelection.visible:
             ZoneDARenderer(self._targetSelection.renderer).fixedStrata = False
             ZoneDARenderer(self._targetSelection.renderer).currentStrata = e.propertyValue == True ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA)
             ZoneClipRenderer(self._targetCenterSelection.renderer).currentStrata = e.propertyValue == True ? int(PlacementStrataEnums.STRATA_NO_Z_ORDER) : int(PlacementStrataEnums.STRATA_AREA)

