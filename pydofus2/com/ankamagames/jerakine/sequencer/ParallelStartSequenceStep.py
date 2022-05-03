from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from com.ankamagames.jerakine.sequencer.ISubSequenceSequencable import (
    ISubSequenceSequencable,
)
from com.ankamagames.jerakine.types.events.SequencerEvent import SequencerEvent

logger = Logger(__name__)


class ParallelStartSequenceStep(AbstractSequencable, ISubSequenceSequencable):

    _aSequence: list[ISequencer]

    _waitAllSequenceEnd: bool

    _waitFirstEndSequence: bool

    _sequenceEndCount: int = 0

    def __init__(
        self,
        aSequence: list,
        waitAllSequenceEnd: bool = True,
        waitFirstEndSequence: bool = False,
    ):
        super().__init__()
        self._aSequence = aSequence
        self._waitAllSequenceEnd = waitAllSequenceEnd
        self._waitFirstEndSequence = waitFirstEndSequence

    def start(self) -> None:
        for i in range(len(self._aSequence)):
            self._aSequence[i].add_listener(SequencerEvent.SEQUENCE_END, self.onSequenceEnd)
            # logger.debug(f"ParallelStartSequenceStep start sequencer {i} that has {self._aSequence[i].steps} steps")
            self._aSequence[i].start()
        if not self._waitAllSequenceEnd and not self._waitFirstEndSequence:
            # logger.debug("first executeCallbacks")
            self.executeCallbacks()

    @property
    def sequenceEndCount(self) -> int:
        return self._sequenceEndCount

    def onSequenceEnd(self, e: SequencerEvent) -> None:
        e.sequencer.remove_listener(SequencerEvent.SEQUENCE_END, self.onSequenceEnd)
        self._sequenceEndCount += 1
        if self._sequenceEndCount == len(self._aSequence):
            self.executeCallbacks()
            self.dispatch(SequencerEvent.SEQUENCE_END, SequencerEvent(SequencerEvent.SEQUENCE_END))
        elif not self._waitAllSequenceEnd:
            if self._sequenceEndCount == 1:
                self.executeCallbacks()
