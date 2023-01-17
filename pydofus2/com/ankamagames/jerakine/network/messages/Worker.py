from whistle import EventDispatcher
from pydofus2.com.ankamagames.jerakine.events.FramePulledEvent import FramePulledEvent
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from time import perf_counter
from types import FunctionType
from pydofus2.com.ankamagames.jerakine.messages.ForTreatment import ForTreatment
from pydofus2.com.ankamagames.jerakine.messages.ForeachTreatment import ForeachTreatment
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.messages.Treatment import Treatment
from pydofus2.com.ankamagames.jerakine.messages.WhileTreatment import WhileTreatment
from pydofus2.com.ankamagames.jerakine.messages.CancelableMessages import CancelableMessage
from pydofus2.com.ankamagames.jerakine.messages.DiscardableMessage import DiscardableMessage
from pydofus2.com.ankamagames.jerakine.messages.MessageHandler import MessageHandler
from pydofus2.com.ankamagames.jerakine.messages.QueueableMessage import QueueableMessage
from pydofus2.com.ankamagames.jerakine.messages.events.FramePushedEvent import FramePushedEvent
from pydofus2.com.ankamagames.jerakine.pools.GenericPool import GenericPool
from pydofus2.com.ankamagames.jerakine.pools.Poolable import Poolable
import pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameDispatcher as efd
from pydofus2.com.ankamagames.jerakine.utils.display.FrameIdManager import FrameIdManager

logger = Logger("Kernel")


class Worker(EventDispatcher, MessageHandler):

    DEBUG_FRAMES: bool = False
    DEBUG_MESSAGES: bool = False
    DEBUG_FRAMES_PROCESSING: bool = False
    LONG_MESSAGE_QUEUE: int = 100
    MAX_TIME_FRAME: int = 40

    def __init__(self):
        self._framesBeingDeleted = dict[Frame, bool]()
        self._messagesQueue = list[Message]()
        self._treatmentsQueue = list[Treatment]()
        self._framesList = list[Frame]()
        self._processingMessage = False
        self._framesToAdd = list[Frame]()
        self._framesToRemove = list[Frame]()
        self._paused = False
        self._pausedQueue = list[Message]()
        self._terminated: bool = False
        self._terminating: bool = False
        self._unstoppableMsgClassList = list()
        self._currentFrameTypesCache = dict()
        super().__init__()

    @property
    def framesList(self) -> list[Frame]:
        return self._framesList

    @property
    def isPaused(self) -> bool:
        return self._paused

    @property
    def pausedQueue(self) -> list[Message]:
        return self._pausedQueue

    @property
    def terminated(self) -> bool:
        return self._terminated

    @property
    def terminating(self) -> bool:
        return self._terminating

    def process(self, msg: Message) -> bool:
        if self._terminated:
            return False
        self._messagesQueue.append(msg)
        self.run()
        return True

    def addSingleTreatmentAtPos(self, object, func: FunctionType, params: list, pos: int) -> None:
        if len(self._treatmentsQueue) == 0:
            efd.EnterFrameDispatcher().addWorker(self)
        self._treatmentsQueue.insert(pos, Treatment(object, func, params))

    def addSingleTreatment(self, object, func: FunctionType, params: list) -> None:
        if len(self._treatmentsQueue) == 0:
            efd.EnterFrameDispatcher().addWorker(self)
        self._treatmentsQueue.append(Treatment(object, func, params))

    def addUniqueSingleTreatment(self, object, func: FunctionType, params: list) -> None:
        if len(self._treatmentsQueue) == 0:
            efd.EnterFrameDispatcher().addWorker(self)
        if not self.hasSingleTreatment(object, func, params):
            self._treatmentsQueue.append(Treatment(object, func, params))

    def addForTreatment(self, object, func: FunctionType, params: list, iterations: int) -> None:
        if iterations == 0:
            return
        if len(self._treatmentsQueue) == 0:
            efd.EnterFrameDispatcher().addWorker(self)
        self._treatmentsQueue.append(ForTreatment(object, func, params, iterations, self))

    def addForeachTreatment(self, object, func: FunctionType, params: list, iterable) -> None:
        if not self._treatmentsQueue:
            efd.EnterFrameDispatcher().addWorker(self)
        self._treatmentsQueue.append(ForeachTreatment(object, func, params, iterable, self))

    def addWhileTreatment(self, object, func: FunctionType, params: list) -> None:
        if not self._treatmentsQueue:
            efd.EnterFrameDispatcher().addWorker(self)
        self._treatmentsQueue.append(WhileTreatment(object, func, params))

    def hasSingleTreatment(self, object, func: FunctionType, params: list) -> bool:
        treatment: Treatment = None
        for treatment in self._treatmentsQueue:
            if treatment.isSameTreatment(object, func, params):
                return True
        return False

    def findTreatments(self, object, func: FunctionType, params: list) -> list:
        treatment: Treatment = None
        result: list = []
        for treatment in self._treatmentsQueue:
            if treatment.isCloseTreatment(object, func, params):
                result.append(treatment)
        return result

    def deleteTreatments(self, treatments: list) -> None:
        for treatment in treatments:
            self._treatmentsQueue.remove(treatment)

    def processImmediately(self, msg: Message) -> bool:
        if self._terminated:
            return False
        self.processMessage(msg)
        return True

    def addFrame(self, frame: Frame) -> None:

        if self._terminated:
            logger.debug(f"[DEBUG WORKER] Cannot add {frame}, worker is terminated")
            return

        if self._currentFrameTypesCache.get(str(frame)):
            frameRemoving = False
            frameAdding = False
            if self._processingMessage:
                for f in self._framesToAdd:
                    if str(f) == str(frame):
                        frameAdding = True
                        break
                if not frameAdding:
                    for f in self._framesToRemove:
                        if str(f) == str(frame):
                            frameRemoving = True
                            break
            if not frameRemoving or frameAdding:
                logger.error(
                    "Someone asked for the frame "
                    + str(frame)
                    + " to be "
                    + "added to the worker, but there is already another "
                    + "frame of the same type within it."
                )
                return

        if not frame:
            return

        if self._processingMessage or self._framesToRemove or self._framesToAdd:
            isAlreadyIn = False
            for f in self._framesToAdd:
                if str(f) == str(frame):
                    isAlreadyIn = True
                    if self.DEBUG_FRAMES:
                        logger.debug(f"[DEBUG WORKER] Frame {frame} already in")
                    break
            if not isAlreadyIn:
                self._framesToAdd.append(frame)
                if self.DEBUG_FRAMES:
                    logger.debug(f"[DEBUG WORKER] >>> Frame {frame} push queued")

        else:
            self.pushFrame(frame)
            if self.DEBUG_FRAMES:
                logger.debug(f"[DEBUG WORKER] >> Frame {frame} pushed")

    def removeFrame(self, frame: Frame) -> None:
        if self._terminated:
            if self.DEBUG_FRAMES:
                logger.debug("[DEBUG WORKER] Cannot remove frame, worker is terminated")
            return

        if not frame:
            return

        if self._processingMessage or self._framesToRemove:
            if self.DEBUG_FRAMES:
                logger.debug(f"[DEBUG WORKER] {frame} queued for deletion")
            self._framesToRemove.append(frame)

        elif not self.isBeingDeleted(frame):
            self._framesBeingDeleted[frame] = True
            self.pullFrame(frame)

    def isBeingDeleted(self, frame: Frame) -> bool:
        return frame in self._framesBeingDeleted

    def isBeingAdded(self, frame: object) -> bool:
        return frame in self._framesToAdd

    def contains(self, frameClassName: str) -> bool:
        return self.getFrame(frameClassName) is not None

    def getFrame(self, frameClassName: str) -> Frame:
        return self._currentFrameTypesCache.get(frameClassName)

    def pause(self, targetobject: object = None, unstoppableMsgobjectList: list = None) -> None:
        logger.debug("[DEBUG WORKER] Worker is paused, all queueable messages will be queued : ")
        self._paused = True
        if unstoppableMsgobjectList:
            self._unstoppableMsgClassList = self._unstoppableMsgClassList.extend(unstoppableMsgobjectList)

    def msgIsUnstoppable(self, msg: Message) -> bool:
        msgobject: object = None
        for msgobject in self._unstoppableMsgClassList:
            if msg is msgobject:
                return True
        return False

    def resume(self) -> None:
        if self._terminated:
            return
        if not self._paused:
            return
        logger.debug("[DEBUG WORKER] Worker is resuming, processing all queued messages.")
        self._paused = False
        self._messagesQueue += self._pausedQueue
        self._pausedQueue = list[Message]()
        self.processFramesInAndOut()
        self.processQueues()

    def terminate(self) -> None:
        self._terminating = True
        self.clear()
        self._terminating = False
        self._terminated = True

    def clear(self) -> None:
        frame: Frame = None
        if self.DEBUG_FRAMES:
            logger.debug("[DEBUG WORKER] Clearing worker (no more frames or messages in queue)")
        nonPulledFrameList = [f for f in self._framesList if not f.pulled()]
        self._framesList.clear()
        self._framesToAdd.clear()
        self._framesToRemove.clear()
        self._messagesQueue.clear()
        self._treatmentsQueue.clear()
        self._pausedQueue.clear()
        self._currentFrameTypesCache.clear()
        self._processingMessage = False
        for frame in nonPulledFrameList:
            self.pushFrame(frame)
        efd.EnterFrameDispatcher().removeWorker()
        self._paused = False

    def onEnterFrame(self) -> None:
        self.processQueues()

    def run(self) -> None:
        efd.EnterFrameDispatcher().addWorker(self)

    def pushFrame(self, frame: Frame) -> None:
        if frame.pushed():
            self._framesList.append(frame)
            self._framesList.sort(key=lambda x: x.priority.value, reverse=True)
            self._currentFrameTypesCache[str(frame)] = frame
            if self.DEBUG_FRAMES:
                logger.warn(f"[DEBUG WORKER] >> Frame {frame} pushed.")
            if self.has_listeners(FramePushedEvent.EVENT_FRAME_PUSHED):
                self.dispatch(FramePushedEvent.EVENT_FRAME_PUSHED, FramePushedEvent(frame))
        else:
            logger.warn(f"[DEBUG WORKER] Frame {frame} refused to be pushed.")

    def logFrameList(self):
        logger.debug(f"[DEBUG WORKER] ew frame list {[str(f) for f in self._framesList]}")

    def logFrameCache(self):
        logger.debug(f"[DEBUG WORKER] new frame cache {[f for f in  self._currentFrameTypesCache]}")

    def pullFrame(self, frame: Frame) -> None:
        if frame.pulled():
            if frame in self._framesList:
                self._framesList.remove(frame)
                if str(frame) in self._currentFrameTypesCache:
                    del self._currentFrameTypesCache[str(frame)]
                if frame in self._framesBeingDeleted:
                    del self._framesBeingDeleted[frame]
                if self.DEBUG_FRAMES:
                    logger.debug(f"[DEBUG WORKER] << Frame {frame} pulled.")
            else:
                if self.DEBUG_FRAMES:
                    logger.warn(f"[DEBUG WORKER] Frame {frame} not in worker frames lsit")
                pass
            if self.has_listeners(FramePulledEvent.EVENT_FRAME_PULLED):
                self.dispatch(FramePulledEvent.EVENT_FRAME_PULLED, FramePulledEvent(frame))
        else:
            logger.warn(f"[DEBUG WORKER] Frame {frame} refused to be pulled.")

    def processQueues(self, maxTime: int = MAX_TIME_FRAME) -> None:
        startTime: int = perf_counter()
        while perf_counter() - startTime < maxTime and (self._messagesQueue or self._treatmentsQueue):
            if self._treatmentsQueue:
                self.processTreatments(startTime, maxTime)
                if not self._treatmentsQueue:
                    self.processFramesInAndOut()
            else:
                msg = self._messagesQueue.pop(0)
                if not (isinstance(msg, CancelableMessage) and msg.cancel):
                    if self._paused and isinstance(msg, QueueableMessage) and not self.msgIsUnstoppable(msg):
                        self._pausedQueue.append(msg)
                        logger.warn(f"[DEBUG WORKER] Queued message: {msg}")
                    else:
                        self.processMessage(msg)
                        if isinstance(msg, Poolable):
                            GenericPool().free(msg)
                        if not self._treatmentsQueue:
                            self.processFramesInAndOut()
        if not self._messagesQueue and not self._treatmentsQueue:
            efd.EnterFrameDispatcher().removeWorker()

    def processTreatments(self, startTime: int, maxTime: int) -> None:
        while perf_counter() - startTime < maxTime and self._treatmentsQueue:
            treatment = self._treatmentsQueue[0]
            if treatment.process():
                self._treatmentsQueue.remove(treatment)

    def avoidFlood(self, omsg: Message) -> bool:
        if len(self._messagesQueue) > self.LONG_MESSAGE_QUEUE:
            toClean = [i for i, msg in enumerate(self._messagesQueue) if msg.__class__.__name__ == omsg.__class__.__name__]
            if len(toClean) > 10:
                for i in toClean:
                    del self._messagesQueue[i]
                return True
        return False

    def processMessage(self, msg: Message) -> None:
        processed: bool = False
        self._processingMessage = True
        for frame in self._framesList:
            if self.DEBUG_FRAMES_PROCESSING:
                logger.debug(f"[DEBUG WORKER] Processing message: {str(msg)} in frame {frame}")
            if frame.process(msg):
                processed = True
                break
        self._processingMessage = False
        if self.DEBUG_MESSAGES:
            logger.debug("[DEBUG WORKER] Message: " + msg.__class__.__name__ + " processed.")
        if not processed and not isinstance(msg, DiscardableMessage):
            logger.debug(
                f"[DEBUG WORKER] Discarded message: {msg.__class__.__name__} (at frame {FrameIdManager().frameId})"
            )

    def processFramesInAndOut(self) -> None:
        if self._framesToRemove:
            for frameToRemove in self._framesToRemove:
                self.pullFrame(frameToRemove)
            self._framesToRemove.clear()
        if self._framesToAdd:
            for frameToAdd in self._framesToAdd:
                self.pushFrame(frameToAdd)
            self._framesToAdd.clear()

    def clearUnstoppableMsgClassList(self) -> None:
        self._unstoppableMsgClassList.clear()

    def removeFrameByName(self, frameName: str) -> None:
        self.removeFrame(self.getFrame(frameName))
