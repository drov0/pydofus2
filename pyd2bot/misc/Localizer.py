import json
from pathlib import Path
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea

from pyd2bot.BotConstants import BotConstants


class BankInfos:
    def __init__(self, npcActionId: int, npcId: float, npcMapId: float, openBankReplyId: int):
        self.npcActionId = npcActionId
        self.npcId = npcId
        self.npcMapId = npcMapId
        self.openBankReplyId = openBankReplyId


class Localizer:
    with open(BotConstants.PERSISTENCE_DIR / "areaInfos.json", "r") as f:
        AREAINFOS: dict = json.load(f)

    @classmethod
    def getBankInfos(cls) -> BankInfos:
        subareaId = MapDisplayManager().currentDataMap.subareaId
        subarea = SubArea.getSubAreaById(subareaId)
        areaId = subarea._area.id
<<<<<<< Updated upstream
        jsonbank = cls.AREAINFOS.get(str(areaId))["bank"]
        return BankInfos(**jsonbank)
=======
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
                    if bankMapId == PlayedCharacterManager().currentMap.mapId:
                        return BankInfos(**jsonbank["bank"])
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
>>>>>>> Stashed changes

    @classmethod
    def getPhenixMapId(cls) -> float:
        subareaId = MapDisplayManager().currentDataMap.subareaId
        subarea = SubArea.getSubAreaById(subareaId)
        areaId = subarea._area.id
        phenixMapId = cls.AREAINFOS.get(str(areaId))["phenixMapId"]
        return phenixMapId
