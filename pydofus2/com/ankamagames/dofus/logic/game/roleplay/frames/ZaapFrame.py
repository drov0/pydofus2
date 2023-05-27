from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.internalDatacenter.taxi.TeleportDestinationWrapper import \
    TeleportDestinationWrapper
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.network.enums.DialogTypeEnum import \
    DialogTypeEnum
from pydofus2.com.ankamagames.dofus.network.enums.TeleporterTypeEnum import \
    TeleporterTypeEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.dialog.LeaveDialogMessage import \
    LeaveDialogMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.TeleportDestinationsMessage import \
    TeleportDestinationsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.TeleportRequestMessage import \
    TeleportRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.ZaapDestinationsMessage import \
    ZaapDestinationsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.ZaapRespawnSaveRequestMessage import \
    ZaapRespawnSaveRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.ZaapRespawnUpdatedMessage import \
    ZaapRespawnUpdatedMessage
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class ZaapFrame(Frame):
    _spawnMapId = 0
    _zaapsList = []

    def __init__(self):
        super().__init__()

    @property
    def spawnMapId(self):
        return self._spawnMapId

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self):
        self._zaapsList = list[TeleportDestinationWrapper]()
        return True
    
    def pulled(self) -> bool:
        return True

    def teleportRequest(self, cost, sourceType, destinationType, mapId):
        if cost <= PlayedCharacterManager().characteristics.kamas:
            trmsg = TeleportRequestMessage()
            trmsg.init(sourceType, destinationType, mapId)
            ConnectionsHandler().send(trmsg)
        else:
            Logger().warning(I18n.getUiText("ui.popup.not_enough_rich"))
            return False
        return True

    def zaapRespawnSaveRequest(self):
        zrsrmsg = ZaapRespawnSaveRequestMessage()
        ConnectionsHandler().send(zrsrmsg)
        return True

    def isZaapKnown(self, mapId):
        for zaap in self._zaapsList:
            if zaap.mapId == mapId:
                return True
        return False
    
    def process(self, msg):

        if isinstance(msg, ZaapDestinationsMessage):
            zdmsg = msg
            self._zaapsList = []
            for dest in zdmsg.destinations:
                self._zaapsList.append(
                    TeleportDestinationWrapper(
                        zdmsg.type,
                        dest.mapId,
                        dest.subAreaId,
                        dest.type,
                        dest.level,
                        dest.cost,
                        zdmsg.spawnMapId == dest.mapId,
                    )
                )
            self._spawnMapId = zdmsg.spawnMapId
            KernelEventsManager().send(
                KernelEvent.TeleportDestinationList,
                self._zaapsList,
                TeleporterTypeEnum.TELEPORTER_HAVENBAG
                if zdmsg.type == TeleporterTypeEnum.TELEPORTER_HAVENBAG
                else TeleporterTypeEnum.TELEPORTER_ZAAP,
            )
            return True

        elif isinstance(msg, TeleportDestinationsMessage):
            tdmsg = msg
            destinations = []
            if tdmsg.type == TeleporterTypeEnum.TELEPORTER_SUBWAY:
                for dest in tdmsg.destinations:
                    hints = TeleportDestinationWrapper.getHintsFromMapId(dest.mapId)
                    for hint in hints:
                        destinations.append(
                            TeleportDestinationWrapper(
                                tdmsg.type,
                                dest.mapId,
                                dest.subAreaId,
                                TeleporterTypeEnum.TELEPORTER_SUBWAY,
                                dest.level,
                                dest.cost,
                                False,
                                hint,
                            )
                        )
            else:
                for dest in tdmsg.destinations:
                    destinations.append(
                        TeleportDestinationWrapper(
                            tdmsg.type, dest.mapId, dest.subAreaId, dest.type, dest.level, dest.cost
                        )
                    )
            KernelEventsManager().send(KernelEvent.TeleportDestinationList, destinations, tdmsg.type)
            return True

        elif isinstance(msg, ZaapRespawnUpdatedMessage):
            zrumsg = msg
            for zaap in self._zaapsList:
                zaap.spawn = zaap.mapId == zrumsg.mapId
            self._spawnMapId = zrumsg.mapId
            KernelEventsManager().send(
                KernelEvent.TeleportDestinationList, self._zaapsList, TeleporterTypeEnum.TELEPORTER_ZAAP
            )
            
        elif isinstance(msg, LeaveDialogMessage):
            if msg.dialogType == DialogTypeEnum.DIALOG_TELEPORTER:
                Kernel().worker.removeFrame(self);
            return True;