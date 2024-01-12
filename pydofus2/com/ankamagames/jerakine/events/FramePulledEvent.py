class FramePulledEvent:
    EVENT_FRAME_PULLED = "framePulled"

    def __init__(self, frame):
        super().__init__()
        self.frame = frame
