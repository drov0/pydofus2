from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from whistle import EventDispatcher


class KernelEventsManager(EventDispatcher, metaclass=Singleton):
    def __init__(self):
        super().__init__()

    MOVEMENT_STOPPED = "movementStopped"
