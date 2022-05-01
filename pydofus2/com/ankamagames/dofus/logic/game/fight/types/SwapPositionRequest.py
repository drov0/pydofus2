class SwapPositionRequest:

    _instanceName: str

    _timelineInstanceName: str

    _isRequesterIcon: bool

    requestId: int

    requesterId: float

    requestedId: float

    def __init__(self, pRequestId: int, pRequesterId: float, pRequestedId: float):
        super().__init__()
        self.requestId = pRequestId
        self.requesterId = pRequesterId
        self.requestedId = pRequestedId
        self._instanceName = "swapPositionRequest#" + pRequestId
        self._timelineInstanceName = "timeline_" + self._instanceName
