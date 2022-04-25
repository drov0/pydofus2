from typing import TYPE_CHECKING
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import (
    InteractiveElement,
)
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.dofus.kernel.Kernel import Kernel

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class FarmAPI(metaclass=Singleton):
    VERBOSE = True
    id = "FarmAPI"

    def __init__(self) -> None:
        pass

    @property
    def rplInteractivesFrame(self) -> "RoleplayInteractivesFrame":
        return Kernel().getWorker().getFrame("RoleplayInteractivesFrame")

    def collectResource(self, elementId: int = None) -> None:
        ce = None
        if elementId is None:
            for it in self.rplInteractivesFrame.collectables.values():
                if it.enabled:
                    ce = it
                    elementId = it.id
                    break
        else:
            ce = self.rplInteractivesFrame.collectables.get(elementId)

        if ce is not None and ce.enabled:
            if self.VERBOSE:
                logger.info(f"[{self.id}] Collecting {ce} ...")
            ie = self.rplInteractivesFrame.interactives.get(elementId)
            if ie is None:
                raise Exception(f"[{self.id}] InteractiveElement {elementId} not found")
            self.rplInteractivesFrame.skillClicked(
                ie, ce.interactiveSkill.skillInstanceUid
            )
            return elementId
        return -1

    def listCollectables(self):
        return self.rplInteractivesFrame._collectableIe
