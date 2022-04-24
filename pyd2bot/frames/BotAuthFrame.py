from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.connection.actions.ServerSelectionAction import (
    ServerSelectionAction,
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
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority

logger = Logger(__name__)


class BotAuthFrame(Frame):
    def __init__(self, serverId, characterId):
        self.serverId = serverId
        self.characterId = characterId
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOW

    def pushed(self) -> bool:
        self._worker = Kernel().getWorker()
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, ServersListMessage):
            self._worker.process(ServerSelectionAction.create(serverId=self.serverId))
            return True

        elif isinstance(msg, CharactersListMessage):
            self._worker.process(
                CharacterSelectionAction.create(
                    characterId=self.characterId, btutoriel=False
                )
            )
            return True
