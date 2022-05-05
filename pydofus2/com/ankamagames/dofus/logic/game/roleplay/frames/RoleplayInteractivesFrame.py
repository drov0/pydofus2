from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.interactives.Interactive import Interactive
from com.ankamagames.dofus.datacenter.jobs.Skill import Skill
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
import com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame as rpeF
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame import (
    RoleplayWorldFrame,
)
from com.ankamagames.dofus.logic.game.roleplay.messages.InteractiveElementActivationMessage import (
    InteractiveElementActivationMessage,
)
from com.ankamagames.dofus.network.enums.MapObstacleStateEnum import (
    MapObstacleStateEnum,
)
from com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import (
    GameContextDestroyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapObstacleUpdateMessage import (
    MapObstacleUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveElementUpdatedMessage import (
    InteractiveElementUpdatedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveMapUpdateMessage import (
    InteractiveMapUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseEndedMessage import (
    InteractiveUseEndedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import (
    InteractiveUsedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.StatedElementUpdatedMessage import (
    StatedElementUpdatedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.StatedMapUpdateMessage import (
    StatedMapUpdateMessage,
)
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import (
    InteractiveElement,
)
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElementSkill import (
    InteractiveElementSkill,
)
from com.ankamagames.dofus.network.types.game.interactive.StatedElement import (
    StatedElement,
)
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

logger = Logger(__name__)


class CollectableElement:
    def __init__(self, id: int, interactiveSkill: InteractiveElementSkill, enabled: bool):
        self.id = id
        self.skill = Skill.getSkillById(interactiveSkill.skillId)
        self.skillName = self.skill.name
        self.interactiveSkill = interactiveSkill
        self.enabled = enabled

    def __str__(self):
        return "CollectableElement(id={}, skill={}, SkillUID={}, enabled={})".format(
            self.id,
            self.skillName,
            self.interactiveSkill.skillInstanceUid,
            self.enabled,
        )


class InteractiveElementData:
    def __init__(self, element: InteractiveElement, position: MapPoint, firstSkill: int) -> None:
        self.element = element
        self.position = position
        self.firstSkill = firstSkill


class RoleplayInteractivesFrame(Frame):

    INTERACTIVE_CURSOR_DISABLED_INDEX: int = 999

    INTERACTIVE_CURSOR_WAIT_INDEX: int = 1000

    cursorList: list = list()

    cursorClassList: list

    INTERACTIVE_CURSOR_NAME: str = "interactiveCursor"

    LUMINOSITY_FACTOR: float = 1.2

    ALPHA_MODIFICATOR: float = 0.2

    COLLECTABLE_COLLECTING_STATE_ID: int = 2

    COLLECTABLE_CUT_STATE_ID: int = 1

    ACTION_COLLECTABLE_RESOURCES: int = 1

    _highlightInteractiveElements: bool

    _modContextMenu: object

    _ie: dict[int, InteractiveElementData]

    _currentUsages: list

    _baseAlpha: float

    i: int

    _entities: dict

    _usingInteractive: bool = False

    _nextInteractiveUsed: object = None

    _interactiveActionTimers: dict

    _enableWorldInteraction: bool = True

    _collectableSpritesToBeStopped: dict

    _currentRequestedElementId: int = -1

    _currentUsedElementId: int = -1

    _statedElementsTargetAnimation: dict

    _mouseDown: bool

    _collectableIe = dict[int, dict]()

    dirmov: int = 666

    def __init__(self):
        self._ie = dict[int, InteractiveElementData]()
        self._collectableIe = dict[int, CollectableElement]()
        self._currentUsages = list()
        self._entities = dict()
        self._interactiveActionTimers = dict()
        self._collectableSpritesToBeStopped = dict()
        self._statedElementsTargetAnimation = dict()
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGH

    @property
    def roleplayWorldFrame(self) -> RoleplayWorldFrame:
        return Kernel().getWorker().getFrame("RoleplayWorldFrame")

    @property
    def currentRequestedElementId(self) -> int:
        return self._currentRequestedElementId

    @currentRequestedElementId.setter
    def currentRequestedElementId(self, pElementId: int) -> None:
        self._currentRequestedElementId = pElementId

    @property
    def usingInteractive(self) -> bool:
        return self._usingInteractive

    @usingInteractive.setter
    def usingInteractive(self, pUsing: bool) -> None:
        self._usingInteractive = pUsing

    @property
    def nextInteractiveUsed(self) -> object:
        return self._nextInteractiveUsed

    @nextInteractiveUsed.setter
    def nextInteractiveUsed(self, object: object) -> None:
        self._nextInteractiveUsed = object

    @property
    def worldInteractionIsEnable(self) -> bool:
        return self._enableWorldInteraction

    @property
    def interactives(self) -> dict[int, InteractiveElementData]:
        return self._ie

    @property
    def collectables(self) -> dict[int, CollectableElement]:
        return self._collectableIe

    def pushed(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, InteractiveMapUpdateMessage):
            imumsg = msg
            self.clear()
            for ie in imumsg.interactiveElements:
                if ie.enabledSkills:
                    self.registerInteractive(ie, ie.enabledSkills[0].skillInstanceUid)
                elif ie.disabledSkills:
                    self.registerInteractive(ie, ie.disabledSkills[0].skillInstanceUid)
            return True

        if isinstance(msg, InteractiveElementUpdatedMessage):
            ieumsg = msg
            if len(ieumsg.interactiveElement.enabledSkills):
                self.registerInteractive(
                    ieumsg.interactiveElement,
                    ieumsg.interactiveElement.enabledSkills[0].skillInstanceUid,
                )
            elif len(ieumsg.interactiveElement.disabledSkills):
                self.registerInteractive(
                    ieumsg.interactiveElement,
                    ieumsg.interactiveElement.disabledSkills[0].skillInstanceUid,
                )
            else:
                self.removeInteractive(ieumsg.interactiveElement)
            return True

        if isinstance(msg, InteractiveUsedMessage):
            iumsg = msg
            if PlayedCharacterManager().id == iumsg.entityId and iumsg.duration > 0:
                self._currentUsedElementId = iumsg.elemId
            if self._currentRequestedElementId == iumsg.elemId:
                self._currentRequestedElementId = -1
            if iumsg.duration > 0:
                if PlayedCharacterManager().id == iumsg.entityId:
                    self._usingInteractive = True
                    rwf = self.roleplayWorldFrame
                    if rwf:
                        rwf.cellClickEnabled = False
                self._entities[iumsg.elemId] = iumsg.entityId
                logger.debug(
                    f"[RolePlayInteractives] Interactive element {iumsg.elemId} is being used by the Entity '{'CurrentPlayer' if iumsg.entityId == PlayedCharacterManager().id else iumsg.entityId}'"
                )
            return False

        if isinstance(msg, InteractiveUseErrorMessage):
            iuem = msg
            if iuem.elemId == self._currentRequestedElementId:
                self._currentRequestedElementId = -1
                # TODO: Send error message to player
            return False

        if isinstance(msg, StatedMapUpdateMessage):
            smumsg = msg
            self._usingInteractive = False
            for se in smumsg.statedElements:
                self.updateStatedElement(se, True)
            return True

        if isinstance(msg, StatedElementUpdatedMessage):
            seumsg = msg
            self.updateStatedElement(seumsg.statedElement)
            return True

        if isinstance(msg, MapObstacleUpdateMessage):
            moumsg = msg
            for mo in moumsg.obstacles:
                InteractiveCellManager().updateCell(
                    mo.obstacleCellId, mo.state == MapObstacleStateEnum.OBSTACLE_OPENED
                )
            return True

        if isinstance(msg, InteractiveUseEndedMessage):
            iuemsg = msg
            self.interactiveUsageFinished(self._entities[iuemsg.elemId], iuemsg.elemId, iuemsg.skillId)
            del self._entities[iuemsg.elemId]
            del self._collectableIe[iuemsg.elemId]
            return False

        if isinstance(msg, GameContextDestroyMessage):
            return False

        return False

    def pulled(self) -> bool:
        self._entities = dict()
        self._ie = dict[int, InteractiveElementData]()
        self._modContextMenu = None
        self._currentUsages = list()
        self._nextInteractiveUsed = None
        self._interactiveActionTimers = dict()
        self._collectableIe = dict[int, CollectableElement]()
        return True

    def enableWorldInteraction(self, pEnable: bool) -> None:
        self._enableWorldInteraction = pEnable

    def clear(self) -> None:
        for timeout in self._currentUsages:
            clearTimeout(timeout)
        self._ie.clear()
        self._collectableIe.clear()

    def getInteractiveElementsCells(self) -> list[int]:
        cells = [cellObj.position.cellId for cellObj in self._ie.values() if cellObj is not None]
        return cells

    def getInteractiveActionTimer(self, pUser) -> BenchmarkTimer:
        return self._interactiveActionTimers[pUser]

    def getInteractiveElement(self, elementId: int) -> InteractiveElementData:
        return self._ie.get(elementId)

    def registerInteractive(self, ie: InteractiveElement, firstSkill: int) -> None:
        if not MapDisplayManager().isIdentifiedElement(ie.elementId):
            return
        entitiesFrame: rpeF.RoleplayEntitiesFrame = Kernel().getWorker().getFrame("RoleplayEntitiesFrame")
        if entitiesFrame:
            found = False
            for s, cie in enumerate(entitiesFrame.interactiveElements):
                if cie.elementId == ie.elementId:
                    found = True
                    entitiesFrame.interactiveElements[int(s)] = ie
            if not found:
                entitiesFrame.interactiveElements.append(ie)
        worldPos: MapPoint = MapDisplayManager().getIdentifiedElementPosition(ie.elementId)
        self._ie[ie.elementId] = InteractiveElementData(ie, worldPos, firstSkill)

    def removeInteractive(self, ie: InteractiveElement) -> None:
        if self._ie.get(ie.elementId):
            del self._ie[ie.elementId]

    def isCollectable(self, ie: InteractiveElement) -> CollectableElement:
        interactive = Interactive.getInteractiveById(ie.elementTypeId)
        if interactive is not None:
            for interactiveSkill in ie.enabledSkills:
                skill = Skill.getSkillById(interactiveSkill.skillId)
                if skill.elementActionId == self.ACTION_COLLECTABLE_RESOURCES:
                    return CollectableElement(ie.elementId, interactiveSkill, True)
            for interactiveSkill in ie.disabledSkills:
                skill = Skill.getSkillById(interactiveSkill.skillId)
                if skill.elementActionId == self.ACTION_COLLECTABLE_RESOURCES:
                    return CollectableElement(ie.elementId, interactiveSkill, False)
        return None

    def updateStatedElement(self, se: StatedElement, globalv: bool = False) -> None:
        if se.elementId == self._currentUsedElementId:
            self._usingInteractive = True
        if se.elementId in self._ie and self._ie[se.elementId].element.onCurrentMap:
            collectable = self.isCollectable(self._ie[se.elementId].element)
            if collectable is not None:
                self._collectableIe[collectable.id] = collectable

    def canBeCollected(self, elementId: int) -> CollectableElement:
        return self._collectableIe.get(elementId)

    def skillClicked(self, ie: InteractiveElementData) -> None:
        msg: InteractiveElementActivationMessage = InteractiveElementActivationMessage(
            ie.element, ie.position, ie.firstSkill
        )
        Kernel().getWorker().process(msg)

    def interactiveUsageFinished(self, entityId: float, elementId: int, skillId: int) -> None:
        if entityId == PlayedCharacterManager().id:
            if self.roleplayWorldFrame:
                self.roleplayWorldFrame.cellClickEnabled = True
            self._usingInteractive = False
            self._currentUsedElementId = -1
            if self._nextInteractiveUsed:
                ieamsg = InteractiveElementActivationMessage(
                    self._nextInteractiveUsed.ie,
                    self._nextInteractiveUsed.position,
                    self._nextInteractiveUsed.skillInstanceId,
                )
                self._nextInteractiveUsed = None
                Kernel().getWorker().process(ieamsg)
