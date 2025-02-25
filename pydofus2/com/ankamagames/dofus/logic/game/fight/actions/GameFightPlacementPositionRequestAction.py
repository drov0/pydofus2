from sys import argv
from pydofus2.com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from pydofus2.com.ankamagames.jerakine.handlers.messages.Action import Action


class GameFightPlacementPositionRequestAction(AbstractAction, Action):

    cellId: int

    def __init__(self, params: list = None):
        super().__init__(params)

    @classmethod
    def create(cls, id: int) -> "GameFightPlacementPositionRequestAction":
        a: GameFightPlacementPositionRequestAction = GameFightPlacementPositionRequestAction(argv)
        a.cellId = id
        return a
