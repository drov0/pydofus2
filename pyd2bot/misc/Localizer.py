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
        jsonbank = cls.AREAINFOS.get(str(areaId))["bank"]
        return BankInfos(**jsonbank)

    @classmethod
    def getPhenixMapId(cls) -> float:
        subareaId = MapDisplayManager().currentDataMap.subareaId
        subarea = SubArea.getSubAreaById(subareaId)
        areaId = subarea._area.id
        phenixMapId = cls.AREAINFOS.get(str(areaId))["phenixMapId"]
        return phenixMapId
