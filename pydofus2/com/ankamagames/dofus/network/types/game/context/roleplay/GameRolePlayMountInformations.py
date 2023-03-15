from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayNamedActorInformations import GameRolePlayNamedActorInformations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.look.EntityLook import EntityLook
    from pydofus2.com.ankamagames.dofus.network.types.game.context.EntityDispositionInformations import EntityDispositionInformations
    

class GameRolePlayMountInformations(GameRolePlayNamedActorInformations):
    ownerName: str
    level: int
    def init(self, ownerName_: str, level_: int, name_: str, look_: 'EntityLook', contextualId_: int, disposition_: 'EntityDispositionInformations'):
        self.ownerName = ownerName_
        self.level = level_
        
        super().init(name_, look_, contextualId_, disposition_)
    