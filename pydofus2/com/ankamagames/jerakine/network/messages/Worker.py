import queue
import threading
import time

from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import \
    MemoryProfiler
from pydofus2.com.ankamagames.jerakine.messages.DiscardableMessage import \
    DiscardableMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.messages.MessageHandler import \
    MessageHandler

"""
This Class for handling messages and frames in a Dofus 2 game application. The worker class is a subclass of MessageHandler and
provides methods for processing messages, adding and removing frames, checking if a frame is present, getting a frame, and terminating the worker. 
The class uses the threading module for handling concurrency, and also uses several classes from the pydofus2 package, such as KernelEventsManager,
Logger, Frame, and Message. There are also several class-level variables for enabling debug logging for frames, messages, and frame processing.
"""
from typing import Optional, Type, TypeVar

T = TypeVar("T", bound="Frame")
class Worker(MessageHandler):
    DEBUG_FRAMES: bool = False
    DEBUG_MESSAGES: bool = False
    DEBUG_FRAMES_PROCESSING: bool = False
    LOCK = threading.Lock()
    CONDITION = threading.Condition(LOCK)
    LAST_TIME = time.perf_counter()
    WANTED_GAP = 1 / 7

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
            # current_time = time.perf_counter()
            # with Worker.LOCK:
            #     time_delta = Worker.WANTED_GAP - (current_time - Worker.LAST_TIME)
            # if time_delta > 0:
            #     self._terminating.wait(time_delta)
            # with Worker.LOCK:
            #     Worker.LAST_TIME = current_time
            msg = self._queue.get()
            # Logger().debug(f"[Worker] [RCV] {msg}")
            self.processFramesInAndOut()
            self.processMessage(msg)
        self._terminated.set()
            
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
                Logger().error(f"[WORKER] Tried to queue Frame '{frame}' but it's already in the queue!")
                return
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
        return self.getFrameByName(frameClassName)

    def getFrameByType(self, frameType: Type[T]) -> Optional[T]:
        frameClassName = frameType.__name__
        return self._currentFrameTypesCache.get(frameClassName)
    
    def getFrameByName(self, frameClassName: str) -> Optional[Frame]:
        return self._currentFrameTypesCache.get(frameClassName)

    def terminate(self) -> None:
        self._terminating.set()
        self._terminated.wait(30)
        self.reset()

    def reset(self) -> None:
        for f in self._framesList:
            f.pulled()
        self._framesList.clear()
        self._framesToAdd.clear()
        self._framesToRemove.clear()
        self._currentFrameTypesCache.clear()
        self._processingMessage.clear()
        self._processingMessage.clear()
 

    def pushFrame(self, frame: Frame) -> None:
        if str(frame) in [str(f) for f in self._framesList]:
            Logger().warn(f"[WORKER] Frame '{frame}' is already in the list.")
            return
        if frame.pushed():
            self._framesList.append(frame)
            self._framesList.sort()
            self._currentFrameTypesCache[str(frame)] = frame
            KernelEventsManager().send(KernelEvent.FRAME_PUSHED, frame)
        else:
            Logger().warn(f"[WORKER] Frame '{frame}' refused to be pushed.")

    def pullFrame(self, frame: Frame) -> None:
        if frame.pulled():
            strFramesList = [str(f) for f in self._framesList]
            while str(frame) in strFramesList:
                idx = strFramesList.index(str(frame))
                strFramesList.pop(idx)
                self._framesList.pop(idx)
            if frame in self._framesList:
                self._framesList.remove(frame)
            if str(frame) in self._currentFrameTypesCache:
                del self._currentFrameTypesCache[str(frame)]
            if frame in self._framesBeingDeleted:
                self._framesBeingDeleted.remove(frame)
            KernelEventsManager().send(KernelEvent.FRAME_PULLED, frame)
        else:
            Logger().warn(f"[WORKER] Frame {frame} refused to be pulled.")

    def processMessage(self, msg: Message) -> None:
        processed: bool = False
        self._processingMessage.set()
        for frame in self._framesList:
            if self._terminated.is_set():
                return
            if frame.process(msg):
                processed = True
                break
        self._processingMessage.clear()
        if not processed and not isinstance(msg, DiscardableMessage):
            raise Exception(f"[WORKER] Discarded message: {msg}!")

    def processFramesInAndOut(self) -> None:
        while self._framesToRemove and not self._terminated.is_set():
            f = self._framesToRemove.pop()
            self.pullFrame(f)
        while self._framesToAdd and not self._terminated.is_set():
            f = self._framesToAdd.pop()
            self.pushFrame(f)

    def removeFrameByName(self, frameName: str) -> None:
        if not self.getFrameByName(frameName):
            Logger().warn(f"[WORKER] Tried to remove frame '{frameName}' but it doesn't exist in cache.")
            return
        self.removeFrame(self.getFrameByName(frameName))
