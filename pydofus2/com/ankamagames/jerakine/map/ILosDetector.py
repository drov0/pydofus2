from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.jerakine.map.IDataMapProvider import IDataMapProvider
    from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint


class ILosDetector:
    def losBetween(
        cls, mapProvider: "IDataMapProvider", refPos: "MapPoint", targetPos: "MapPoint", tested: dict[str, bool] = {}
    ) -> bool:
        raise NotImplementedError()
