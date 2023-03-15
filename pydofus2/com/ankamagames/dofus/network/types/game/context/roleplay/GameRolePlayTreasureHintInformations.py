from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayActorInformations import GameRolePlayActorInformations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.look.EntityLook import EntityLook
    from pydofus2.com.ankamagames.dofus.network.types.game.context.EntityDispositionInformations import EntityDispositionInformations
    

class GameRolePlayTreasureHintInformations(GameRolePlayActorInformations):
    npcId: int
    def init(self, npcId_: int, look_: 'EntityLook', contextualId_: int, disposition_: 'EntityDispositionInformations'):
        self.npcId = npcId_
        
        super().init(look_, contextualId_, disposition_)
    