class GroupMemberLuaData:

    def __init__(self, pLevel: int, pIsCompanion: bool, pIsStillPresentInFight: bool):
        self.level = pLevel
        self.isCompanion = pIsCompanion
        self.isStillPresentInFight = pIsStillPresentInFight

    def __str__(self):
        return f"level={self.level};isCompanion={self.isCompanion};isStillPresentInFight={self.isStillPresentInFight};"
