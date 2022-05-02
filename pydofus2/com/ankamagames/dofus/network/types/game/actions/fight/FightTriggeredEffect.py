from com.ankamagames.dofus.network.types.game.actions.fight.AbstractFightDispellableEffect import (
    AbstractFightDispellableEffect,
)


class FightTriggeredEffect(AbstractFightDispellableEffect):
    diceNum: int = 0
    diceSide: int = 0
    value: int = 0
    delay: int = 0

    def init(
        self,
        param1_: int,
        param2_: int,
        param3_: int,
        delay_: int,
        uid_: int,
        targetId_: int,
        turnDuration_: int,
        dispelable_: int,
        spellId_: int,
        effectId_: int,
        parentBoostUid_: int,
    ):
        self.diceNum = param1_
        self.diceSide = param2_
        self.value = param3_
        self.delay = delay_

        super().__init__(
            uid_,
            targetId_,
            turnDuration_,
            dispelable_,
            spellId_,
            effectId_,
            parentBoostUid_,
        )
