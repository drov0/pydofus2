from pydofus2.com.ankamagames.dofus.network.messages.game.character.choice.BasicCharactersListMessage import BasicCharactersListMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.character.choice.CharacterBaseInformations import CharacterBaseInformations
    

class CharactersListMessage(BasicCharactersListMessage):
    hasStartupActions: bool
    def init(self, hasStartupActions_: bool, characters_: list['CharacterBaseInformations']):
        self.hasStartupActions = hasStartupActions_
        
        super().init(characters_)
    