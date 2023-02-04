import queue
import threading

from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import KernelEvent, KernelEventsManager
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import MemoryProfiler
from pydofus2.com.ankamagames.jerakine.messages.DiscardableMessage import DiscardableMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.messages.MessageHandler import MessageHandler

"""
This Class for handling messages and frames in a Dofus 2 game application. The worker class is a subclass of MessageHandler and
provides methods for processing messages, adding and removing frames, checking if a frame is present, getting a frame, and terminating the worker. 
The class uses the threading module for handling concurrency, and also uses several classes from the pydofus2 package, such as KernelEventsManager,
Logger, Frame, and Message. There are also several class-level variables for enabling debug logging for frames, messages, and frame processing.
"""
from typing import Optional, Type, TypeVar, cast
T = TypeVar("T", bound="Frame")

class Worker(MessageHandler):
    DEBUG_FRAMES: bool = False
    DEBUG_MESSAGES: bool = False
    DEBUG_FRAMES_PROCESSING: bool = False

    def __init__(self):
        self._framesBeingDeleted = set[Frame]()
        self._framesList = list[Frame]()
        self._processingMessage = threading.Event()
        self._framesToAdd = set[Frame]()
        self._framesToRemove = set[Frame]()
        self._terminated = threading.Event()
        self._terminating = threading.Event()
        self._currentFrameTypesCache = dict[str, Frame]()
        self._queue = queue.Queue()

    @property
    def terminated(self) -> threading.Event:
        return self._terminated

    def run(self) -> None:
        while not self._terminating.is_set():
            msg = self._queue.get()
            self.processFramesInAndOut()
            self.processMessage(msg)

    def process(self, msg: Message) -> bool:
        if self._terminated.is_set():
            return
        self._queue.put(msg)

    def addFrame(self, frame: Frame) -> None:
        if self._terminated.is_set() or frame is None:
            Logger().warning(f"Can't add frame {frame} because the worker is terminated")
            return

        if str(frame) in self._currentFrameTypesCache:
            if frame in self._framesToAdd and frame not in self._framesToRemove:
                raise Exception(f"Can't add the frame '{frame}' because it's already in the to-add list.")

        if self._processingMessage.is_set():
            if frame in self._framesToAdd:
                raise Exception(f"[WORKER] Tried to queue Frame '{frame}' but it's already in the queue!")
            if self.DEBUG_FRAMES:
                Logger().debug(f"[WORKER] >>> Queuing Frame {frame} for addition...")
            self._framesToAdd.add(frame)

        else:
            self.pushFrame(frame)

    def removeFrame(self, frame: Frame) -> None:
        if self._terminated.is_set() or frame is None:
            return

        if self._processingMessage.is_set():
            if frame not in self._framesToRemove:
                self._framesToRemove.add(frame)
                if self.DEBUG_FRAMES:
                    Logger().debug(f"[WORKER] >>> Frame {frame} remove queued...")
                    
        elif frame not in self._framesBeingDeleted:
            self._framesBeingDeleted.add(frame)
            self.pullFrame(frame)

    def contains(self, frameClassName: str) -> bool:
        return self.getFrame(frameClassName) is not None

    def getFrameByType(self, frameType: Type[T]) -> Optional[T]:
        frameClassName = frameType.__name__
        return self._currentFrameTypesCache.get(frameClassName)
    
    def getFrame(self, frameClassName: str) -> Optional[Frame]:
        return self._currentFrameTypesCache.get(frameClassName)

    def terminate(self) -> None:
        self._terminating.set()
        self.reset()
        self._terminating.clear()
        self._terminated.set()

    def reset(self) -> None:
        nonPulledFrameList = [f for f in self._framesList if not f.pulled()]
        self._framesList.clear()
        self._framesToAdd.clear()
        self._framesToRemove.clear()
        self._currentFrameTypesCache.clear()
        self._processingMessage.clear()
        for frame in nonPulledFrameList:
            raise Exception(f"[WORKER] Frame '{frame}' was not pulled!")

    def pushFrame(self, frame: Frame) -> None:
        if self.DEBUG_FRAMES:
            Logger().debug(
                f"[WORKER] >> Frames list before push: {[(str(f), f.priority.value) for f in self._framesList]}"
            )
        if frame.pushed():
            self._framesList.append(frame)
            self._framesList.sort()
            self._currentFrameTypesCache[str(frame)] = frame
            if self.DEBUG_FRAMES:
                Logger().warn(f"[WORKER] >> Frame '{frame}' pushed.")
            if self.DEBUG_FRAMES:
                Logger().debug(
                    f"[WORKER] >> Frames list after push: {[(str(f), f.priority.value) for f in self._framesList]}"
                )
            KernelEventsManager().send(KernelEvent.FRAME_PUSHED, frame)
        else:
            Logger().warn(f"[WORKER] Frame '{frame}' refused to be pushed.")

    def logFrameList(self):
        Logger().debug(f"[WORKER] new frame list {[str(f) for f in self._framesList]}")

    def logFrameCache(self):
        Logger().debug(f"[WORKER] new frame cache {[f for f in  self._currentFrameTypesCache]}")

    def pullFrame(self, frame: Frame) -> None:
        if frame.pulled():
            if frame in self._framesList:
                self._framesList.remove(frame)
            else:
                if self.DEBUG_FRAMES:
                    Logger().warn(f"[WORKER] Frame {frame} not in worker frames lsit")
            if str(frame) in self._currentFrameTypesCache:
                del self._currentFrameTypesCache[str(frame)]
            if frame in self._framesBeingDeleted:
                self._framesBeingDeleted.remove(frame)
            if self.DEBUG_FRAMES:
                Logger().debug(f"[WORKER] << Frame {frame} pulled.")
            KernelEventsManager().send(KernelEvent.FRAME_PULLED, frame)
        else:
            Logger().warn(f"[WORKER] Frame {frame} refused to be pulled.")

    @MemoryProfiler.track_memory("Worker.processMessage")
    def processMessage(self, msg: Message) -> None:
        processed: bool = False
        self._processingMessage.set()
        if self.DEBUG_MESSAGES:
            Logger().debug(f"[WORKER] Message: {msg.__class__.__name__} is being processed...")
        for frame in self._framesList:
            if self._terminated.is_set():
                return
            if self.DEBUG_FRAMES_PROCESSING:
                Logger().debug(f"[WORKER] Processing message: {str(msg)} in frame {frame}")
            if frame.process(msg):
                processed = True
                break
        self._processingMessage.clear()
        if self.DEBUG_MESSAGES:
            Logger().debug(f"[WORKER] Message: {msg.__class__.__name__} processed.")
        if not processed and not isinstance(msg, DiscardableMessage):
            raise Exception(f"[WORKER] Discarded message: {msg.__class__.__name__}!")

    @MemoryProfiler.track_memory("Worker.processFrames")
    def processFramesInAndOut(self) -> None:
        while self._framesToRemove and not self._terminated.is_set():
            f = self._framesToRemove.pop()
            self.pullFrame(f)
        while self._framesToAdd and not self._terminated.is_set():
            f = self._framesToAdd.pop()
            self.pushFrame(f)

    def removeFrameByName(self, frameName: str) -> None:
        if not self.getFrame(frameName):
            return
        self.removeFrame(self.getFrame(frameName))
