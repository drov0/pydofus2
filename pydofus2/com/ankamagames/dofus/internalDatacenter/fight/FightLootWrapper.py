from com.ankamagames.dofus.internalDatacenter.items.ItemWrapper import ItemWrapper
from com.ankamagames.dofus.network.types.game.context.fight.FightLoot import FightLoot
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffect import (
    ObjectEffect,
)
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter


class FightLootWrapper(IDataCenter):

    objects: list

    kamas: float = 0

    def __init__(self, loot: FightLoot):
        super().__init__()
        self.objects = list()
        for i in range(0, len(loot.objects), 2):
            self.objects.append(
                ItemWrapper.create(
                    63,
                    0,
                    loot.objects[i],
                    loot.objects[i + 1],
                    list[ObjectEffect](),
                    False,
                )
            )
        self.kamas = loot.kamas
