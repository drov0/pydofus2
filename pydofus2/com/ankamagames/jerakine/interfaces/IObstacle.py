class IObstacle:
    @property
    def canSeeThrough(self) -> bool:
        raise NotImplementedError()

    @property
    def canWalkThrough(self) -> bool:
        raise NotImplementedError()

    @property
    def canWalkTo(self) -> bool:
        raise NotImplementedError()
