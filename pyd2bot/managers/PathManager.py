import json
import os
from pathlib import Path
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

CURRDIR = Path(__file__).parent
PATHSDB = CURRDIR / "pathsDB.json"


class PathManager:
    if not os.path.exists(PATHSDB):
        with open(PATHSDB, "w") as fp:
            json.dump({}, fp)
    with open(PATHSDB, "r") as fp:
        _db = json.load(fp)

    @classmethod
    def addEntry(cls, subAreaId, mapId, mapRpZone, fightOnly=True, jobIds=[]):
        if not fightOnly and not jobIds:
            raise Exception("You must specify a jobIds if you don't fightOnly")
        MapDisplayManager().loadMap(mapId)
        subareaId = MapDisplayManager().currentDataMap.subareaId
        print(f"SubareaId: {subareaId}")

        aubAreId = SubArea.getSubAreaById(subareaId)

        cls._db.update(
            {
                "subAreaId": subAreaId,
                "startVertex": {"mapId": mapId, "mapRpZone": mapRpZone},
                "fightOnly": fightOnly,
                "jobIds": jobIds,
            }
        )
        with open(PATHSDB, "w") as fp:
            json.dump(cls._db, fp, indent=4)

    @classmethod
    def getEntry(cls, name):
        result = cls._db.get(name)
        return result


if __name__ == "__main__":
    import sys

    botName = sys.argv[1]
    account = sys.argv[2]
    serverId = int(sys.argv[3])
    charachterId = int(sys.argv[4])
    BotCredsManager.addEntry(botName, account, charachterId, serverId)
