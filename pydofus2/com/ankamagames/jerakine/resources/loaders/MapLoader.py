from functools import lru_cache
from pathlib import Path
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.dataAdapter.dlm import DLM

logger = Logger("Dofus2")


class MapLoader(metaclass=Singleton):
    DLM_KEY = Constants.DLM_ENCRYPTION_KEY
    logger.debug(f"Maps encryption key: {DLM_KEY}")

    def __init__(self) -> None:
        self._reader = DLM(self.DLM_KEY)

    @lru_cache(maxsize=5)
    def load(self, mapId, key=None):
        if key is not None:
            self._reader.setKey(key)
        map_p = Path(Constants.MAPS_PATH) / MapLoader.getMapURI(mapId)
        if not map_p.exists():
            raise Exception(f"Map {mapId} not found in path {map_p}")
        with open(map_p, "rb") as f:
            compressedMapBinary = f.read()
            return self._reader.read(compressedMapBinary)

    def getMapURI(mapId):
        return f"{int(mapId) % 10}/{int(mapId)}.dlm"
