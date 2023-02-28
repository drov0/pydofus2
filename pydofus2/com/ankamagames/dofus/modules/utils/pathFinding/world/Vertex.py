class Vertex:
    _mapId: float

    _zoneId: int

    _uid: float

    def __init__(self, mapId: float, zoneId: int, vertexUid: float):
        super().__init__()
        self._mapId = mapId
        self._zoneId = zoneId
        self._uid = vertexUid

    @property
    def mapId(self) -> float:
        return self._mapId

    @property
    def zoneId(self) -> int:
        return self._zoneId

    @property
    def UID(self) -> float:
        return self._uid

    def __hash__(self) -> int:
        return self.UID
    
    def __eq__(self, o: 'Vertex') -> bool:
        return self.UID == o.UID
    
    def __str__(self) -> str:
        return f"Vertex(mapId={self._mapId}, zoneId={self._zoneId}, uid={self._uid})"

    def to_json(self) -> dict:
        return {
            "mapId": self._mapId,
            "zoneId": self._zoneId,
            "vertexUid": self._uid,
        }
