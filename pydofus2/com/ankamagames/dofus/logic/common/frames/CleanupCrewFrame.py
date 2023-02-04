
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class CleanupCrewFrame(Frame):
    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOWEST

    def pushed(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:
        # Logger().info(f"[Warning] {msg.__class__.__name__} wasn't stopped by a frame.")
        return True

    def pulled(self) -> bool:
        return True
