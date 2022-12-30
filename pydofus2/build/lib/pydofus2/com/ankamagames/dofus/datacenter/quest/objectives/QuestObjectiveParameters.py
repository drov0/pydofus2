
class QuestObjectiveParameters:

    numParams:int

    parameter0:int

    parameter1:int

    parameter2:int

    parameter3:int

    parameter4:int

    dungeonOnly:bool

    def __init__(self):
        super().__init__()

    def __getitem__(self, name):
        propertyName:str = str(name)
        try:
            int(propertyName)
            return getattr(self, f"parameter{propertyName}")
        except ValueError:
            return getattr(self, propertyName)
    
    @property
    def length(self) -> int:
        return self.numParams


