from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.connection.actions.ServerSelectionAction import (
    ServerSelectionAction,
)
from com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import (
    AuthentificationManager,
)
from com.ankamagames.dofus.logic.game.approach.actions.CharacterSelectionAction import (
    CharacterSelectionAction,
)
from com.ankamagames.dofus.network.messages.connection.ServersListMessage import (
    ServersListMessage,
)
from com.ankamagames.dofus.network.messages.game.character.choice.CharactersListMessage import (
    CharactersListMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
import threading

logger = Logger("Dofus2")


class BotGameApproach(Frame):
    def __init__(self, characterId):
        self.characterId = characterId
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOW

    def pushed(self) -> bool:
        self._worker = Kernel().getWorker()
        return True

    def pulled(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:
        if isinstance(msg, ServersListMessage):
            self._worker.process(ServerSelectionAction.create(AuthentificationManager()._lva.serverId))
            return True

        elif isinstance(msg, CharactersListMessage):
            self._worker.process(CharacterSelectionAction.create(characterId=self.characterId, btutoriel=False))
            return True
