class ItemCriterionOperator:

    SUPERIOR = ">"
    INFERIOR = "<"
    EQUAL = "="
    DIFFERENT = "!"
    EQUIPPED = "E"
    NOT_EQUIPPED = "X"
    OPERATORS_LIST = [
        SUPERIOR,
        INFERIOR,
        EQUAL,
        DIFFERENT,
        "#",
        "~",
        "s",
        "S",
        "e",
        "E",
        "v",
        "i",
        "X",
        "/",
    ]
    _operator: str

    def __init__(self, pstrOperator: str):
        self._operator = pstrOperator

    @property
    def text(self) -> str:
        return self._operator

    @property
    def htmlText(self) -> str:
        if self._operator == self.SUPERIOR:
            return "&gt"
        if self._operator == self.INFERIOR:
            return "&lt"
        return self._operator

    def compare(self, pLeftMember: float, pRightMember: float) -> bool:
        if self._operator == self.SUPERIOR:
            if pLeftMember > pRightMember:
                return True
        elif self._operator == self.INFERIOR:
            if pLeftMember < pRightMember:
                return True
        elif self._operator == self.EQUAL:
            if pLeftMember == pRightMember:
                return True
        elif self._operator == self.DIFFERENT:
            if pLeftMember != pRightMember:
                return True
        return False
