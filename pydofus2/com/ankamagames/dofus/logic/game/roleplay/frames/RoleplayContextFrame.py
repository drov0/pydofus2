from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from com.ankamagames.dofus.internalDatacenter.world.WorldPointWrapper import (
    WorldPointWrapper,
)
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
import com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame as ref
import com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame as rif
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import (
    RoleplayMovementFrame,
)
import com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame as rplWF
from com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import (
    GameContextDestroyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapInstanceMessage import (
    CurrentMapInstanceMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapMessage import (
    CurrentMapMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObtainedItemMessage import ObtainedItemMessage
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority

logger = Logger("Dofus2")


class RoleplayContextFrame(Frame):
    def __init__(self):
        self._newCurrentMapIsReceived = False
        self._previousMapId = None
        self._priority = Priority.NORMAL
        self._listMapNpcsMsg = []
        super().__init__()

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, p: int) -> None:
        self._priority = p

    @property
    def previousMapId(self) -> float:
        return self._previousMapId

    @property
    def newCurrentMapIsReceived(self) -> bool:
        return self._newCurrentMapIsReceived

    @newCurrentMapIsReceived.setter
    def newCurrentMapIsReceived(self, value: bool) -> None:
        self._newCurrentMapIsReceived = value

    @property
    def entitiesFrame(self) -> ref.RoleplayEntitiesFrame:
        return self._entitiesFrame

    def pushed(self) -> bool:
        self._movementFrame = RoleplayMovementFrame()
        self._worldFrame = rplWF.RoleplayWorldFrame()
        self._entitiesFrame = ref.RoleplayEntitiesFrame()
        self._interactivesFrame = rif.RoleplayInteractivesFrame()
        logger.debug("RoleplayContextFrame pushed")
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, CurrentMapMessage):
            mcmsg = msg
            logger.debug(f"[RoleplayContext] Loading roleplay map {mcmsg.mapId}")
            self._newCurrentMapIsReceived = True
            newSubArea = SubArea.getSubAreaByMapId(mcmsg.mapId)
            PlayedCharacterManager().currentSubArea = newSubArea
            if isinstance(mcmsg, CurrentMapInstanceMessage):
                MapDisplayManager().mapInstanceId = mcmsg.instantiatedMapId
            else:
                MapDisplayManager().mapInstanceId = 0
            wp = None
            if self._entitiesFrame and Kernel().getWorker().contains("RoleplayEntitiesFrame"):
                Kernel().getWorker().removeFrame(self._entitiesFrame)
            if self._worldFrame and Kernel().getWorker().contains("RoleplayWorldFrame"):
                Kernel().getWorker().removeFrame(self._worldFrame)
            if self._interactivesFrame and Kernel().getWorker().contains("RoleplayInteractivesFrame"):
                Kernel().getWorker().removeFrame(self._interactivesFrame)
            if self._movementFrame and Kernel().getWorker().contains("RoleplayMovementFrame"):
                Kernel().getWorker().removeFrame(self._movementFrame)
            if PlayedCharacterManager().isInHouse:
                wp = WorldPointWrapper(
                    mcmsg.mapId,
                    True,
                    PlayedCharacterManager().currentMap.outdoorX,
                    PlayedCharacterManager().currentMap.outdoorY,
                )
            else:
                wp = WorldPointWrapper(int(mcmsg.mapId))
            if PlayedCharacterManager().currentMap:
                self._previousMapId = PlayedCharacterManager().currentMap.mapId
            PlayedCharacterManager().currentMap = wp
            MapDisplayManager().loadMap(int(mcmsg.mapId))
            return False

        elif isinstance(msg, MapLoadedMessage):
            logger.debug("[RoleplayContext] Map loaded will push other roleplay frames")
            Kernel().getWorker().addFrame(self._entitiesFrame)
            Kernel().getWorker().addFrame(self._worldFrame)
            Kernel().getWorker().addFrame(self._movementFrame)
            Kernel().getWorker().addFrame(self._interactivesFrame)
            # Kernel().getWorker().process(self._listMapNpcsMsg)
            self._listMapNpcsMsg = None
            return True

        elif isinstance(msg, GameContextDestroyMessage):
            logger.debug("RoleplayContextFrame: will be retrieved from kernel cause switching to fight")
            Kernel().getWorker().removeFrame(self)
            return False

        elif isinstance(msg, ObtainedItemMessage):
            return True

        return False

    def pulled(self) -> bool:
        self._interactivesFrame.clear()
        Kernel().getWorker().removeFrame(self._entitiesFrame)
        # Kernel().getWorker().removeFrame(self._delayedActionFrame)
        Kernel().getWorker().removeFrame(self._worldFrame)
        Kernel().getWorker().removeFrame(self._movementFrame)
        Kernel().getWorker().removeFrame(self._interactivesFrame)
        logger.debug("RoleplayContextFrame pulled")
        # TODO : Don't forget to uncomment this when those frames are implemented dumpass
        # Kernel().getWorker().removeFrame(self._spectatorManagementFrame)
        # Kernel().getWorker().removeFrame(self._npcDialogFrame)
        # Kernel().getWorker().removeFrame(self._documentFrame)
        # Kernel().getWorker().removeFrame(self._zaapFrame)
        # Kernel().getWorker().removeFrame(self._paddockFrame)
        # if Kernel().getWorker().contains("HavenbagFrame"):
        #     Kernel().getWorker().removeFrame(Kernel().getWorker().getFrame("HavenbagFrame"))
        return True
