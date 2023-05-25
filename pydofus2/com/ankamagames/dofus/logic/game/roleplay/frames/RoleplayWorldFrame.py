from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import \
    AnimatedCharacter
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class RoleplayWorldFrame(Frame):
    
    NO_CURSOR: int = -1
    FIGHT_CURSOR: int = 3
    NPC_CURSOR: int = 1
    DIRECTIONAL_PANEL_ID: int = 316
    _playerEntity: AnimatedCharacter
    _playerName: str
    _allowOnlyCharacterInteraction: bool
    pivotingCharacter: bool

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:
        return False

    def pulled(self) -> bool:
        return True
