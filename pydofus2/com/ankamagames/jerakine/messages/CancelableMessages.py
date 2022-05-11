class CancelableMessage:
    @property
    def cancel(self) -> bool:
        raise NotImplementedError()
