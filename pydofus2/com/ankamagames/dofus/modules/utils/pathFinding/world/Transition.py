from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.GroupItemCriterion import GroupItemCriterion
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.TransitionTypeEnum import TransitionTypeEnum
from pydofus2.com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum


class Transition:

    _type: int

    _direction: int

    _skillId: int

    _criterion: str

    _transitionMapId: float

    _cell: int

    _id: int

    def __init__(
        self,
        type: int,
        direction: int,
        skillId: int,
        criterion: str,
        transitionMapId: float,
        cell: int,
        id: int,
    ):
        super().__init__()
        self._type = type
        self._direction = direction
        self._skillId = skillId
        self._criterion = criterion
        self._transitionMapId = transitionMapId
        self._cell = cell
        self._id = id

    @property
    def type(self) -> int:
        return self._type

    @property
    def direction(self) -> int:
        return self._direction

    @property
    def skillId(self) -> int:
        return self._skillId

    @property
    def criterion(self) -> str:
        return self._criterion

    @property
    def cell(self) -> int:
        return self._cell

    @property
    def transitionMapId(self) -> float:
        return self._transitionMapId

    @property
    def id(self) -> int:
        return self._id

    @property
    def isValid(self) -> bool:
        criterionWhiteList: list = [
            "Ad",
            "DM",
            "MI",
            "Mk",
            "Oc",
            "Pc",
            "QF",
            "Qo",
            "Qs",
            "Sv",
        ]
        if len(self.criterion) != 0:
            if "&" not in self.criterion and "|" not in self.criterion and self.criterion[0:2] in criterionWhiteList:
                return False
            criterion = GroupItemCriterion(self.criterion)
            return criterion.isRespected
        return True

    def __str__(self) -> str:
        return f"Transition(type={TransitionTypeEnum(self._type).name}, direction={DirectionsEnum(self._direction).name}, skillId={self._skillId}, criterion={self._criterion}, transitionMapId={self._transitionMapId}, cell={self._cell}, id={self._id})"

    def to_json(self):
        return {
            "type": self._type,
            "direction": self._direction,
            "skillId": self._skillId,
            "criterion": self._criterion,
            "transitionMapId": self._transitionMapId,
            "cell": self._cell,
            "id": self._id,
        }
