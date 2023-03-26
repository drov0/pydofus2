from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.frames.ChatFrame import \
    ChatFrame
from pydofus2.com.ankamagames.dofus.network.Metadata import Metadata
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.messages.Worker import Worker

if TYPE_CHECKING:
    from pyd2bot.logic.common.frames.BotRPCFrame import BotRPCFrame
    from pyd2bot.logic.roleplay.behaviors.FarmFights import FarmFights
    from pydofus2.com.ankamagames.dofus.logic.connection.frames.AuthentificationFrame import \
        AuthentificationFrame
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import \
        FightBattleFrame
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import \
        FightContextFrame
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import \
        FightEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightTurnFrame import \
        FightTurnFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.PartyFrame import \
        PartyFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import \
        RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import \
        RoleplayInteractivesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import \
        RoleplayMovementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame import \
        RoleplayWorldFrame


class Kernel(metaclass=Singleton):
    def __init__(self) -> None:
        self._worker: Worker = Worker()
        self.beingInReconection: bool = False
        self._reseted = True
        self.isMule = False

    @property
    def worker(self) -> Worker:
        return self._worker

    @property
    def reseted(self) -> bool:
        return self._reseted

    def init(self) -> None:
        if self._reseted:
            Logger().info("Initializing ...")
            self._worker.reset()
            self.addInitialFrames()
            self._reseted = False
            Logger().info(f"Using protocole #{Metadata.PROTOCOL_BUILD}, built on {Metadata.PROTOCOL_DATE}")
            Logger().info("Initialized")

    def reset(
        self,
        autoRetry: bool = False,
        reloadData: bool = False,
    ) -> None:
        from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
            KernelEventsManager
        from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
            ConnectionsHandler
        from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import \
            BenchmarkTimer

        Logger().debug("Resetting ...")
        BenchmarkTimer.reset()
        KernelEventsManager().reset()
        if not reloadData:
            self._worker.terminate()
        else:
            self._worker.reset()
        if ConnectionsHandler().conn and not ConnectionsHandler().conn.closed:
            ConnectionsHandler().closeConnection(DisconnectionReasonEnum.WANTED_SHUTDOWN)
        Singleton.clearAll()
        self.beingInReconection = False
        if reloadData:
            self.beingInReconection = True
            self.addInitialFrames()
        else:
            self._reseted = True
        Logger().debug("Reseted")

    def addInitialFrames(self) -> None:
        from pydofus2.com.ankamagames.dofus.logic.common.frames.CleanupCrewFrame import \
            CleanupCrewFrame
        from pydofus2.com.ankamagames.dofus.logic.common.frames.LatencyFrame import \
            LatencyFrame
        from pydofus2.com.ankamagames.dofus.logic.common.frames.QueueFrame import \
            QueueFrame
        from pydofus2.com.ankamagames.dofus.logic.connection.frames.AuthentificationFrame import \
            AuthentificationFrame
        from pydofus2.com.ankamagames.dofus.logic.connection.frames.DisconnectionHandlerFrame import \
            DisconnectionHandlerFrame

        Logger().info("Adding initial frames ...")
        self._worker.addFrame(LatencyFrame())
        self._worker.addFrame(AuthentificationFrame())
        self._worker.addFrame(QueueFrame())
        self._worker.addFrame(DisconnectionHandlerFrame())
        self._worker.addFrame(CleanupCrewFrame())
        self._worker.addFrame(ChatFrame())
        Logger().info("Initial frames added.")

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return self._worker.getFrameByName("RoleplayMovementFrame")

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return self._worker.getFrameByName("RoleplayEntitiesFrame")

    @property
    def farmFrame(self) -> "FarmFights":
        return self._worker.getFrameByName("BotFarmPathFrame")

    @property
    def rpcFrame(self) -> "BotRPCFrame":
        return self._worker.getFrameByName("BotRPCFrame")

    @property
    def partyFrame(self) -> "PartyFrame":
        return self._worker.getFrameByName("PartyFrame")

    @property
    def interactivesFrame(self) -> "RoleplayInteractivesFrame":
        return self._worker.getFrameByName("RoleplayInteractivesFrame")

    @property
    def worldFrame(self) -> "RoleplayWorldFrame":
        return self._worker.getFrameByName("RoleplayWorldFrame")

    @property
    def fightEntitiesFrame(self) -> "FightEntitiesFrame":
        return self._worker.getFrameByName("FightEntitiesFrame")

    @property
    def battleFrame(self) -> "FightBattleFrame":
        return self._worker.getFrameByName("FightBattleFrame")

    @property
    def turnFrame(self) -> "FightTurnFrame":
        return self._worker.getFrameByName("FightTurnFrame")

    @property
    def fightContextFrame(self) -> "FightContextFrame":
        return self._worker.getFrameByName("FightContextFrame")

    @property
    def authFrame(self) -> "AuthentificationFrame":
        return self._worker.getFrameByName("AuthentificationFrame")