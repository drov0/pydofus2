from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import \
    DataMapProvider
from pydofus2.com.ankamagames.dofus.internalDatacenter.items.ItemWrapper import \
    ItemWrapper
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.network.Metadata import Metadata
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.messages.Worker import Worker

if TYPE_CHECKING:
    from pyd2bot.logic.common.frames.BotRPCFrame import BotRPCFrame
    from pyd2bot.logic.roleplay.behaviors.fight.FarmFights import FarmFights
    from pydofus2.com.ankamagames.dofus.logic.common.frames.AlignmentFrame import \
        AlignmentFrame
    from pydofus2.com.ankamagames.dofus.logic.common.frames.ChatFrame import \
        ChatFrame
    from pydofus2.com.ankamagames.dofus.logic.common.frames.QuestFrame import \
        QuestFrame
    from pydofus2.com.ankamagames.dofus.logic.connection.frames.AuthentificationFrame import \
        AuthentificationFrame
    from pydofus2.com.ankamagames.dofus.logic.connection.frames.ServerSelectionFrame import \
        ServerSelectionFrame
    from pydofus2.com.ankamagames.dofus.logic.game.common.frames.CommonExchangeManagementFrame import \
        CommonExchangeManagementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.common.frames.ExchangeManagementFrame import \
        ExchangeManagementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.common.frames.PlayedCharacterUpdatesFrame import \
        PlayedCharacterUpdatesFrame
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
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayContextFrame import \
        RoleplayContextFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import \
        RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import \
        RoleplayInteractivesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import \
        RoleplayMovementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame import \
        RoleplayWorldFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.ZaapFrame import \
        ZaapFrame


class Kernel(metaclass=Singleton):

    def __init__(self) -> None:
        self._worker: Worker = Worker()
        self.beingInReconection: bool = False
        self._reseted = True
        self.isMule = False
        self.mitm = False

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
        reloadData: bool = False,
    ) -> None:
        from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
            KernelEventsManager
        from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
            ConnectionsHandler
        from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import \
            PlayerManager
        from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import \
            StatsManager
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

        Logger().debug("Resetting ...")
        BenchmarkTimer.reset()
        KernelEventsManager().reset()
        FightersStateManager.clear()
        CurrentPlayedFighterManager.clear()
        DofusEntities.clear()
        ItemWrapper.clearCache()
        PlayedCharacterManager.clear()
        StatsManager.clear()
        PlayerManager.clear()
        DataMapProvider.clear()
        SpellModifiersManager.clear()
        if not reloadData:
            self._worker.terminate()
        else:
            self._worker.reset()
        if ConnectionsHandler().conn and not ConnectionsHandler().conn.closed:
            ConnectionsHandler().closeConnection(DisconnectionReasonEnum.DISCONNECTED_BY_USER)
        self.beingInReconection = False
        if reloadData:
            self.beingInReconection = True
            self.addInitialFrames()
        else:
            Singleton.clearAll()
            self._reseted = True
        Logger().debug("Reseted")

    def addInitialFrames(self) -> None:
        from pydofus2.com.ankamagames.dofus.logic.common.frames.ChatFrame import \
            ChatFrame
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
    def serverSelectionFrame(self) -> "ServerSelectionFrame":
        return self._worker.getFrameByName("ServerSelectionFrame")

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
    def roleplayContextFrame(self) -> "RoleplayContextFrame":
        return self._worker.getFrameByName("RoleplayContextFrame")

    @property
    def authFrame(self) -> "AuthentificationFrame":
        return self._worker.getFrameByName("AuthentificationFrame")

    @property
    def commonExchangeManagementFrame(self) -> "CommonExchangeManagementFrame":
        return self._worker.getFrameByName("CommonExchangeManagementFrame")

    @property
    def craftFrame(self):
        return self._worker.getFrameByName("CraftFrame")

    @property
    def exchangeManagementFrame(self) -> "ExchangeManagementFrame":
        return self.roleplayContextFrame._exchangeManagementFrame

    @property
    def zaapFrame(self) -> "ZaapFrame":
        return self.roleplayContextFrame._zaapFrame

    @property
    def questFrame(self) -> "QuestFrame":
        return self._worker.getFrameByName("QuestFrame")

    @property
    def alignmentFrame(self) -> "AlignmentFrame":
        return self._worker.getFrameByName("AlignmentFrame")

    @property
    def chatFrame(self) -> "ChatFrame":
        return self._worker.getFrameByName("ChatFrame")

    @property
    def playedCharacterUpdatesFrame(self) -> "PlayedCharacterUpdatesFrame":
        return self._worker.getFrameByName("PlayedCharacterUpdatesFrame")
