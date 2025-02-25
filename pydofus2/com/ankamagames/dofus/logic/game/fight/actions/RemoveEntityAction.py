from sys import argv
from pydofus2.com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from pydofus2.com.ankamagames.jerakine.handlers.messages.Action import Action


class RemoveEntityAction(AbstractAction, Action):

    actorId: float

    def __init__(self, params: list = None):
        super().__init__(params)

    @classmethod
    def create(cls, actorId: float) -> "RemoveEntityAction":
        o = RemoveEntityAction(argv)
        o.actorId = actorId
        return o
