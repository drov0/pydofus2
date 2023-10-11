class MountLuaData:

    def __init__(self, pLevel: int = 0, pCoefficient: float = 0.0, pBonusAlmanac: float = 0.0, pWise: float = 1.0):
        self.level = pLevel
        self.coefficient = pCoefficient
        self.bonusAlmanac = pBonusAlmanac
        self.wise = pWise

    def __str__(self):
        return f"level={self.level};coefficient={self.coefficient};bonusAlmanach={self.bonusAlmanac};wise={self.wise};"
