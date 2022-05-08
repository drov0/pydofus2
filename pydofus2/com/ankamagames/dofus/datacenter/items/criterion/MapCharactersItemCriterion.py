from com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import IItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.ItemCriterion import ItemCriterion
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
from com.ankamagames.dofus.network.types.game.context.GameContextActorInformations import GameContextActorInformations
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayActorInformations import (
    GameRolePlayActorInformations,
)
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter


class MapCharactersItemCriterion(ItemCriterion, IDataCenter):

    _mapId: float

    _nbCharacters: int

    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)
        params: list = self._criterionValueText.split(",")
        if len(params) == 1:
            self._mapId = PlayedCharacterManager().currentMap.mapId
            self._nbCharacters = int(params[0])
        elif len(params) == 2:
            self._mapId = float(params[0])
            self._nbCharacters = int(params[1])

    @property
    def text(self) -> str:
        readableCriterionRef: str = I18n.getUiText("ui.criterion.MK", [self._mapId])
        return readableCriterionRef + " " + self._operator.text + " " + self._nbCharacters

    def clone(self) -> IItemCriterion:
        return MapCharactersItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        nbCharacters: int = 0
        entitiesInfos: dict = None
        actorInfo: GameContextActorInformations = None
        entitiesFrame: RoleplayEntitiesFrame = Kernel().getWorker().getFrame("RoleplayEntitiesFrame")
        if entitiesFrame:
            entitiesInfos = entitiesFrame.entities
            for actorInfo in entitiesInfos:
                if isinstance(actorInfo, GameRolePlayActorInformations):
                    nbCharacters += 1
        return nbCharacters
