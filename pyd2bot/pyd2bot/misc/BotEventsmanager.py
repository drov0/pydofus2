from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from whistle import EventDispatcher


class BotEventsManager(EventDispatcher, metaclass=Singleton):

    ALLMEMBERS_ONSAME_MAP = 0

    def __init__(self):
        super().__init__()
