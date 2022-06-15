import json
import os
from pyd2bot.BotConstants import BotConstants
from pyd2bot.models.farmPaths.AbstractFarmPath import AbstractFarmPath
from pyd2bot.models.farmPaths.RandomSubAreaFarmPath import RandomSubAreaFarmPath

PATHSDB = BotConstants.PERSISTENCE_DIR / "paths.json"


class PathManager:
    if not os.path.exists(PATHSDB):
        with open(PATHSDB, "w") as fp:
            json.dump({}, fp)
    with open(PATHSDB, "r") as fp:
        _db = json.load(fp)
    _pathClass = {
        "RandomSubAreaFarmPath": RandomSubAreaFarmPath,
    }

    @classmethod
    def addPath(cls, pathId: str, path: AbstractFarmPath):
        cls._db.update({pathId: path.to_json()})
        with open(PATHSDB, "w") as fp:
            json.dump(cls._db, fp, indent=4)

    @classmethod
    def getPath(cls, pathId: str):
        pathJson = cls._db.get(pathId)
        if pathJson:
            pathCls = cls._pathClass.get(pathJson["type"])
            if pathCls:
                return pathCls.from_json(pathJson)
            raise Exception("Unknown path type: " + pathJson["type"])
        return None


if __name__ == "__main__":
    pass
