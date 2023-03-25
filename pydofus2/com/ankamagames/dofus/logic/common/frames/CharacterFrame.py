from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.actions.ChangeServerAction import \
    ChangeServerAction
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import \
    AuthentificationManager
from pydofus2.com.ankamagames.dofus.network.messages.game.approach.ReloginTokenRequestMessage import \
    ReloginTokenRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.approach.ReloginTokenStatusMessage import \
    ReloginTokenStatusMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.creation.CharacterCreationResultMessage import \
    CharacterCreationResultMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.creation.CharacterNameSuggestionFailureMessage import \
    CharacterNameSuggestionFailureMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.creation.CharacterNameSuggestionSuccessMessage import \
    CharacterNameSuggestionSuccessMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.deletion.CharacterDeletionPrepareMessage import \
    CharacterDeletionPrepareMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class CharacterFrame(Frame):

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self) -> bool:
        self._changeToServerId = None
        return True

    def pulled(sef):
        return True

    def process(self, msg) -> bool:

        if isinstance(msg, ReloginTokenStatusMessage):
            if self._changeToServerId:
                AuthentificationManager()._lva.serverId = self._changeToServerId
                AuthentificationManager().setToken(msg.token)
                ConnectionsHandler().closeConnection(DisconnectionReasonEnum.CHANGING_SERVER)
                self._changeToServerId = None
            KernelEventsManager().send(KernelEvent.RELOGIN_TOKEN, msg.validToken, msg.token)
            return True

        elif isinstance(msg, CharacterCreationResultMessage):
            KernelEventsManager().send(KernelEvent.CHARACTER_CREATION_RESULT, msg.result, msg.reason)
            return True
        
        elif isinstance(msg, CharacterNameSuggestionSuccessMessage):
            KernelEventsManager().send(KernelEvent.CHARACTER_NAME_SUGGESTION, msg.suggestion)
            return True
        
        elif isinstance(msg, CharacterNameSuggestionFailureMessage):
            KernelEventsManager().send(KernelEvent.CHARACTER_NAME_SUGGESTION_FAILED)
            return True

        elif isinstance(msg, ChangeServerAction):
            self._changeToServerId = msg.serverId
            rtrccmsg = ReloginTokenRequestMessage()
            rtrccmsg.init()
            ConnectionsHandler().send(rtrccmsg)
            return True

        elif isinstance(msg, CharacterDeletionPrepareMessage):
            KernelEventsManager().send(KernelEvent.CHAR_DEL_PREP, msg)
            return True
