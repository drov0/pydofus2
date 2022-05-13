import json
from pathlib import Path
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.MapCoordinates import MapCoordinates
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.datacenter.world.Phoenix import Phoenix
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder

from pyd2bot.BotConstants import BotConstants


class BankInfos:
    def __init__(self, npcActionId: int, npcId: float, npcMapId: float, openBankReplyId: int):
        self.npcActionId = npcActionId
        self.npcId = npcId
        self.npcMapId = npcMapId
        self.openBankReplyId = openBankReplyId


class Localizer:
    _phenixesByAreaId = dict[int, list]()
    with open(BotConstants.PERSISTENCE_DIR / "areaInfos.json", "r") as f:
        AREAINFOS: dict = json.load(f)

    @classmethod
    def getBankInfos(cls) -> BankInfos:
        subareaId = MapDisplayManager().currentDataMap.subareaId
        subarea = SubArea.getSubAreaById(subareaId)
        areaId = subarea._area.id
        playerPos = PlayedCharacterManager().currMapPos
        if str(areaId) in cls.AREAINFOS:
            closestBank = cls.AREAINFOS[str(areaId)]["bank"]
        else:
            minDist = float("inf")
            srcV = WorldPathFinder().currPlayerVertex
            closestBank = None
            for areaId, jsonbank in cls.AREAINFOS.items():
                if "bank" in jsonbank:
                    rpZ = 1
                    bankMapId = jsonbank["bank"]["npcMapId"]
                    while True:
                        dstV = WorldPathFinder().worldGraph.getVertex(bankMapId, rpZ)
                        if not dstV:
                            break
                        path = AStar.search(WorldPathFinder().worldGraph, srcV, dstV, lambda x: (), False)
                        if path is not None:
                            bankMapPos = MapPosition.getMapPositionById(bankMapId)
                            dist = abs(bankMapPos.posX - playerPos.posX) + abs(bankMapPos.posY - playerPos.posY)
                            if dist < minDist:
                                dist = len(path)
                                closestBank = jsonbank["bank"]
                            break
                        rpZ += 1
        return BankInfos(**closestBank)

    @classmethod
    def getPhenixMapId(cls) -> float:
        subareaId = MapDisplayManager().currentDataMap.subareaId
        subarea = SubArea.getSubAreaById(subareaId)
        if not cls._phenixesByAreaId:
            for phenix in Phoenix.getAllPhoenixes():
                phenixSubArea = SubArea.getSubAreaByMapId(phenix.mapId)
                if phenixSubArea._area.id not in cls._phenixesByAreaId:
                    cls._phenixesByAreaId[phenixSubArea._area.id] = []
                cls._phenixesByAreaId[phenixSubArea._area.id].append(phenix.mapId)
        minDist = float("inf")
        closestPhenixMapId = None
        playerMp = MapPosition.getMapPositionById(MapDisplayManager().currentMapPoint.mapId)
        for phenixMapId in cls._phenixesByAreaId[subarea._area.id]:
            phenixMp = MapPosition.getMapPositionById(phenixMapId)
            dist = abs(phenixMp.posX - playerMp.posX) + abs(phenixMp.posY - playerMp.posY)
            if dist < minDist:
                minDist = dist
                closestPhenixMapId = phenixMapId
        return closestPhenixMapId
