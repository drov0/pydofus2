import sys
from com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from com.ankamagames.jerakine.handlers.messages.Action import Action


class ChallengeTargetsListRequestAction(AbstractAction, Action):

    challengeId: int

    def __init__(self, params: list = None):
        super().__init__(params)

    @classmethod
    def create(cls, challengeId: int) -> "ChallengeTargetsListRequestAction":
        a: ChallengeTargetsListRequestAction = cls(sys.argv[1:])
        a.challengeId = challengeId
        return a
