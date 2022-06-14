from whistle import EventDispatcher
from pydofus2.com.ankamagames.jerakine.sequencer.ISequencable import ISequencable


class ISubSequenceSequencable(ISequencable, EventDispatcher):
    pass
