from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.character.alteration.AlterationInfo import AlterationInfo


class AlterationAddedMessage(NetworkMessage):
    alteration: "AlterationInfo"

    def init(self, alteration_: "AlterationInfo"):
        self.alteration = alteration_

        super().__init__()
