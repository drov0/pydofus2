from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffect import (
    ObjectEffect,
)


class ObjectEffectDice(ObjectEffect):
    diceNum: int = 0
    diceSide: int = 0
    diceConst: int = 0

    def init(self, diceNum_: int, diceSide_: int, diceConst_: int, actionId_: int):
        self.diceNum = diceNum_
        self.diceSide = diceSide_
        self.diceConst = diceConst_

        super().init(actionId_)
