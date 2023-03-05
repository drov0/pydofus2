from pydofus2.com.ankamagames.dofus.logic.common.frames.ChatFrame import \
    ChatFrame
from pydofus2.com.ankamagames.dofus.network.Metadata import Metadata
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.messages.Worker import Worker


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
            Logger().info("[KERNEL] Initializing ...")
            self._worker.reset()
            self.addInitialFrames()
            self._reseted = False
            Logger().info(f"[KERNEL] Using protocole #{Metadata.PROTOCOL_BUILD}, built on {Metadata.PROTOCOL_DATE}")
            Logger().info("[KERNEL] Initialized")

    def reset(
        self,
        autoRetry: bool = False,
        reloadData: bool = False,
    ) -> None:
        from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import \
            DataMapProvider
        from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
            KernelEventsManager
        from pydofus2.com.ankamagames.dofus.internalDatacenter.items.ItemWrapper import \
            ItemWrapper
        from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
            ConnectionsHandler
        from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import \
            PlayerManager
        from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import \
            StatsManager
        from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import \
            AuthentificationManager
        from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
            PlayedCharacterManager
        from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import \
            DofusEntities
        from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import \
            CurrentPlayedFighterManager
        from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.FightersStateManager import \
            FightersStateManager
        from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.SpellModifiersManager import \
            SpellModifiersManager
        from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import \
            BenchmarkTimer

        Logger().debug("[KERNEL] Resetting ...")
        KernelEventsManager().reset()
        if not autoRetry:
            AuthentificationManager.clear()
        FightersStateManager.clear()
        CurrentPlayedFighterManager.clear()
        DofusEntities().reset()
        ItemWrapper.clearCache()
        PlayedCharacterManager.clear()
        BenchmarkTimer.clear()
        StatsManager.clear()
        PlayerManager.clear()
        DataMapProvider.clear()
        if not reloadData:
            self._worker.terminate()
        if ConnectionsHandler().conn is not None and not ConnectionsHandler().conn.closed:
            ConnectionsHandler().conn.close()
            ConnectionsHandler().conn.join()
        ConnectionsHandler.clear()
        SpellModifiersManager.clear()
        self.beingInReconection = False
        if reloadData:
            self._worker.reset()
            self.addInitialFrames()
        else:
            self._reseted = True
        Logger().debug("[KERNEL] Reseted")

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
        Logger().info("[KERNEL] Adding initial frames ...")
        self._worker.addFrame(LatencyFrame())
        self._worker.addFrame(AuthentificationFrame())
        self._worker.addFrame(QueueFrame())
        self._worker.addFrame(DisconnectionHandlerFrame())
        self._worker.addFrame(CleanupCrewFrame())
        Kernel().worker.addFrame(ChatFrame())
        Logger().info("[KERNEL] Initial frames added.")
