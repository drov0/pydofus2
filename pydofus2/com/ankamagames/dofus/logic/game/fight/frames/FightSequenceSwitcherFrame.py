from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority


class FightSequenceSwitcherFrame(Frame):

    _currentFrame: Frame = None

    def __init__(self):
        super().__init__()

    def pushed(self) -> bool:
        return True

    def pulled(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return Priority.HIGHEST

    @property
    def currentFrame(self) -> Frame:
        return self._currentFrame

    @currentFrame.setter
    def currentFrame(self, f: Frame) -> None:
        self._currentFrame = f

    def process(self, msg: Message) -> bool:
        if self._currentFrame:
            return self._currentFrame.process(msg)
        return False
