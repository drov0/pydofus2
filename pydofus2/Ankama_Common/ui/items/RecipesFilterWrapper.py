class RecipesFilterWrapper:

    def __init__(self, pjobId: int, pminLevel: int, pmaxLevel: int, ptypeId: int = 0):
        self.jobId = pjobId
        self.minLevel = pminLevel
        self.maxLevel = pmaxLevel
        self.typeId = ptypeId
