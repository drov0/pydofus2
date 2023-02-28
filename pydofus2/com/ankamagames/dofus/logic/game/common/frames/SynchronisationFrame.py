from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.network.enums.GameContextEnum import \
    GameContextEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.basic.SequenceNumberMessage import \
    SequenceNumberMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.basic.SequenceNumberRequestMessage import \
    SequenceNumberRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameContextCreateMessage import \
    GameContextCreateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapMessage import \
    CurrentMapMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import \
        RoleplayMovementFrame


class SynchronisationFrame(Frame):

    STEP_TIME: int = 2

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGHEST

    def pushed(self) -> bool:
        self._synchroStepByServer = dict()
        return True

    def resetSynchroStepByServer(self, connexionId: str) -> None:
        self._synchroStepByServer[connexionId] = 0

    def process(self, msg: Message) -> bool:
        snrMsg: SequenceNumberRequestMessage = None
        snMsg: SequenceNumberMessage = None

        if isinstance(msg, SequenceNumberRequestMessage):
            snrMsg = msg
            if not self._synchroStepByServer.get(snrMsg.sourceConnection):
                self._synchroStepByServer[snrMsg.sourceConnection] = 0
            self._synchroStepByServer[snrMsg.sourceConnection] += 1
            snMsg = SequenceNumberMessage()
            snMsg.init(number_=self._synchroStepByServer[snrMsg.sourceConnection])
            ConnectionsHandler().send(snMsg)
            return True

        if isinstance(msg, CurrentMapMessage):
            rplmvf: "RoleplayMovementFrame" = Kernel().worker.getFrameByName("RoleplayMovementFrame")
            if rplmvf and rplmvf.requestTimer:
                rplmvf.requestTimer.cancel()
                rplmvf.requestingMapChange = None
                rplmvf._changeMapFails = 0
            return False

        if isinstance(msg, GameContextCreateMessage):
            if msg.context == GameContextEnum.FIGHT:
                rplmvf: "RoleplayMovementFrame" = Kernel().worker.getFrameByName("RoleplayMovementFrame")
                if rplmvf and rplmvf.requestTimer:
                    rplmvf.requestTimer.cancel()
                    rplmvf._requestFighFails = 0
                    rplmvf.requestingAtackMonsters = None
                if rplmvf and rplmvf._joinFightTimer:
                    rplmvf._joinFightTimer.cancel()
                if rplmvf and rplmvf.movementAnimTimer:
                    rplmvf.movementAnimTimer.cancel()
            return False

        else:
            return False

    def pulled(self) -> bool:
        return True
