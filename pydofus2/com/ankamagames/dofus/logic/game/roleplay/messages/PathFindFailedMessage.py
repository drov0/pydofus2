from pydofus2.com.ankamagames.jerakine.messages.Message import Message


class PathFindFailed(Message):

    _src: int

    _dest: int

    def __init__(self, src: int, dest: int):
        super().__init__()
        self._src = src
        self._dest = dest

    @property
    def src(self) -> float:
        return self._src

    @property
    def dest(self) -> int:
        return self._dest
