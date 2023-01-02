from pydofus2.com.ankamagames.jerakine.messages.MessageHandler import MessageHandler
from pydofus2.com.ankamagames.jerakine.utils.misc.Priotizable import Prioritizable


class Frame(MessageHandler, Prioritizable):
    def pushed(self) -> bool:
        pass

    def pulled(self) -> bool:
        pass

    def __str__(self):
        return self.__class__.__name__
