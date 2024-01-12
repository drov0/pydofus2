from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame


class FramePushedEvent:

    EVENT_FRAME_PUSHED = "event_frame.appended"

    _frame: Frame

    def __init__(self, frame: Frame):
        super().__init__(self.EVENT_FRAME_PUSHED, False, False)
        self._frame = frame

    @property
    def frame(self) -> Frame:
        return self._frame
