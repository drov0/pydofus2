class IDataMapProvider:
    @property
    def width(self) -> int:
        pass

    @property
    def height(self) -> int:
        pass

    def pointLos(self, x: int, y: int, bAllowTroughEntity: bool = True) -> bool:
        pass

    def pointMov(
        self,
        x: int,
        y: int,
        allowThroughtEntity: bool = True,
        cellId: int = -1,
        endCellId: int = -1,
        avoidObstacles: bool = True,
    ) -> bool:
        pass

    def farmCell(self, param1: int, param2: int) -> bool:
        pass

    def pointSpecialEffects(self, param1: int, param2: int) -> int:
        pass

    def pointWeight(self, param1: int, param2: int, param3: bool = True) -> float:
        pass

    def hasEntity(self, x: int, y: int, allowThroughtEntity: bool = False) -> bool:
        pass

    def updateCellMovLov(self, param1: int, param2: bool) -> None:
        pass

    def isChangeZone(self, param1: int, param2: int) -> bool:
        pass

    def getCellSpeed(self, param1: int) -> int:
        pass

    def fillEntityOnCellArray(self, param1: list[bool], param2: bool) -> list[bool]:
        pass
