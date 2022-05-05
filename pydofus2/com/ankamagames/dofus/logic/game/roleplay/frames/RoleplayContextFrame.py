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
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority

logger = Logger(__name__)


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
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, CurrentMapMessage):
            mcmsg = msg
            self._newCurrentMapIsReceived = True
            newSubArea = SubArea.getSubAreaByMapId(mcmsg.mapId)
            PlayedCharacterManager().currentSubArea = newSubArea
            logger.debug(f"Roleplay received current map, will pause the connextion until its loaded")
            Kernel().getWorker().pause(None)
            ConnectionsHandler.pause()
            if isinstance(mcmsg, CurrentMapInstanceMessage):
                MapDisplayManager().mapInstanceId = mcmsg.instantiatedMapId
            else:
                MapDisplayManager().mapInstanceId = 0
            wp = None
            # Kernel().getWorker().logFrameCache()
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
            self._entitiesFrame._waitForMap = True
            MapDisplayManager().loadMap(int(mcmsg.mapId))
            return False

        elif isinstance(msg, MapLoadedMessage):
            logger.debug("Roleplay received map loaded message, will resume the connection")
            Kernel().getWorker().resume()
            Kernel().getWorker().clearUnstoppableMsgClassList()
            ConnectionsHandler.resume()
            # Kernel().getWorker().logFrameCache()
            if not Kernel().getWorker().contains("RoleplayEntitiesFrame"):
                Kernel().getWorker().addFrame(self._entitiesFrame)
            if not Kernel().getWorker().contains("RoleplayInteractivesFrame"):
                Kernel().getWorker().addFrame(self._interactivesFrame)
            if not Kernel().getWorker().contains("RoleplayMovementFrame"):
                Kernel().getWorker().addFrame(self._movementFrame)
            if not Kernel().getWorker().contains("RoleplayWorldFrame"):
                Kernel().getWorker().addFrame(self._worldFrame)
            Kernel().getWorker().logFrameCache()
            # SurveyManager.getInstance().checkSurveys()
            if self._listMapNpcsMsg:
                Kernel().getWorker().process(self._listMapNpcsMsg)
                self._listMapNpcsMsg = None
            return True

        elif isinstance(msg, GameContextDestroyMessage):
            Kernel().getWorker().removeFrame(self)
            return True

        elif isinstance(msg, ObtainedItemMessage):
            return True

        return False

    def pulled(self) -> bool:
        return True
