from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import \
    MapDisplayManager
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.datacenter.interactives.Interactive import \
    Interactive
from pydofus2.com.ankamagames.dofus.datacenter.jobs.Skill import Skill
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.network.enums.MapObstacleStateEnum import \
    MapObstacleStateEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import \
    GameContextDestroyMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapObstacleUpdateMessage import \
    MapObstacleUpdateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveElementUpdatedMessage import \
    InteractiveElementUpdatedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveMapUpdateMessage import \
    InteractiveMapUpdateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import \
    InteractiveUsedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseEndedMessage import \
    InteractiveUseEndedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import \
    InteractiveUseErrorMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.StatedElementUpdatedMessage import \
    StatedElementUpdatedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.StatedMapUpdateMessage import \
    StatedMapUpdateMessage
from pydofus2.com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import \
    InteractiveElement
from pydofus2.com.ankamagames.dofus.network.types.game.interactive.InteractiveElementSkill import \
    InteractiveElementSkill
from pydofus2.com.ankamagames.dofus.network.types.game.interactive.StatedElement import \
    StatedElement
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import \
        RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import \
        RoleplayMovementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame import \
        RoleplayWorldFrame


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
    def __init__(self, element: InteractiveElement, position: MapPoint, skillUID: int) -> None:
        self.element = element
        self.position = position
        self.skillUID = skillUID


class RoleplayInteractivesFrame(Frame):

    COLLECTABLE_COLLECTING_STATE_ID: int = 2

    COLLECTABLE_CUT_STATE_ID: int = 1

    ACTION_COLLECTABLE_RESOURCES: int = 1

    REVIVE_SKILL_ID = 211
    
    REQUEST_TIMEOUT = 10

    def __init__(self):
        self._usingInteractive: bool = False
        self._ie = dict[int, InteractiveElementData]()
        self._collectableIe = dict[int, CollectableElement]()
        self._currentUsages = list()
        self._enityUsingElement = dict()
        self._interactiveActionTimers = dict()
        self._statedElementsTargetAnimation = dict()
        self.currentRequestedElementId: int = -1
        self._currentUsedElementId: int = -1
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGH

    @property
    def roleplayWorldFrame(self) -> "RoleplayWorldFrame":
        return Kernel().worker.getFrameByName("RoleplayWorldFrame")

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return Kernel().worker.getFrameByName("RoleplayMovementFrame")
    
    @property
    def interactives(self) -> dict[int, InteractiveElementData]:
        return self._ie

    @property
    def collectables(self) -> dict[int, CollectableElement]:
        return self._collectableIe

    def pushed(self) -> bool:
        Logger().debug("RoleplayInteractivesFrame pushed")
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
            if msg.duration > 0:
                self._enityUsingElement[msg.elemId] = msg.entityId
                KernelEventsManager().send(KernelEvent.INTERACTIVE_ELEMENT_BEING_USED, msg.entityId, msg.elemId)
                if msg.entityId == PlayedCharacterManager().id:                
                    Logger().info(f"[RolePlayInteractives] Player is using element {msg.elemId} ...")
                    self.usingInteractive = True
            else:
                if msg.entityId == PlayedCharacterManager().id:    
                    Logger().info(f"[RolePlayInteractives] Player is used element {msg.elemId}")
                KernelEventsManager().send(KernelEvent.INTERACTIVE_ELEMENT_USED, msg.entityId, msg.elemId)
            return True
        
        if isinstance(msg, InteractiveUseEndedMessage):
            Logger().info(f"[RolePlayInteractives] Interactive element {msg.elemId} used.")
            if msg.entityId == PlayedCharacterManager().id:
                self.usingInteractive = False
            KernelEventsManager().send(KernelEvent.INTERACTIVE_ELEMENT_USED, self._enityUsingElement[msg.elemId], msg.elemId)            
            del self._enityUsingElement[msg.elemId]
            del self._collectableIe[msg.elemId]
            return True
        
        if isinstance(msg, InteractiveUseErrorMessage):
            iuem = msg
            if iuem.elemId == self.currentRequestedElementId:
                self.currentRequestedElementId = -1
            KernelEventsManager().send(KernelEvent.INTERACTIVE_USE_ERROR, msg.elemId)
            return True

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

        if isinstance(msg, GameContextDestroyMessage):
            return False

        return False

    def pulled(self) -> bool:
        self._enityUsingElement.clear()
        self._ie.clear()
        self._currentUsages.clear()
        self._interactiveActionTimers.clear()
        self._collectableIe.clear()
        return True

    def clear(self) -> None:
        self._ie.clear()
        self._collectableIe.clear()

    def getInteractiveElementsCells(self) -> list[int]:
        cells = [cellObj.position.cellId for cellObj in self._ie.values() if cellObj is not None]
        return cells

    def getInteractiveElement(self, elementId: int, skillId=None) -> InteractiveElementData:
        ie = self._ie.get(elementId)
        if skillId is not None and ie is not None:
            for skill in ie.element.enabledSkills:
                if skill.skillId == skillId:
                    ie.skillUID = skill.skillInstanceUid
        return ie

    def registerInteractive(self, ie: InteractiveElement, firstSkill: int) -> None:
        if not MapDisplayManager().isIdentifiedElement(ie.elementId):
            return
        entitiesFrame: "RoleplayEntitiesFrame" = Kernel().worker.getFrameByName("RoleplayEntitiesFrame")
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

    def getReviveIe(self) -> InteractiveElementData:
        return self.getIeBySkillId(self.REVIVE_SKILL_ID)

    def getIeBySkillId(self, skillId: int) -> InteractiveElementData:
        for ie in self._ie.values():
            if ie.element.enabledSkills:
                for skill in ie.element.enabledSkills:
                    if skill.skillId == skillId:
                        ie.skillUID = skill.skillInstanceUid
                        return ie

    def updateStatedElement(self, se: StatedElement, globalv: bool = False) -> None:
        if se.elementId == self._currentUsedElementId:
            self._usingInteractive = True
        if se.elementId in self._ie and self._ie[se.elementId].element.onCurrentMap:
            collectable = self.isCollectable(self._ie[se.elementId].element)
            if collectable is not None:
                self._collectableIe[collectable.id] = collectable

    def canBeCollected(self, elementId: int) -> CollectableElement:
        return self._collectableIe.get(elementId)
