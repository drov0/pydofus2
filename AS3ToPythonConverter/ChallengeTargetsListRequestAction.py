from com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from com.ankamagames.jerakine.handlers.messages.Action import Action

class ChallengeTargetsListRequestAction(AbstractAction, Action):

    challengeId:int

    def __init__(self, params:list = None):
        super().__init__(params)

    def create(self, challengeId:int) -> ChallengeTargetsListRequestAction:
        a:ChallengeTargetsListRequestAction = ChallengeTargetsListRequestAction(arguments)
        a.challengeId = challengeId
        return a


