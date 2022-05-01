from com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from com.ankamagames.jerakine.handlers.messages.Action import Action

class SpellVariantActivationRequestAction(AbstractAction, Action):

    spellId:int

    def __init__(self, params:list = None):
        super().__init__(params)

    def create(self, spellId:int) -> SpellVariantActivationRequestAction:
        a:SpellVariantActivationRequestAction = SpellVariantActivationRequestAction(arguments)
        a.spellId = spellId
        return a


