from typing import Any


class ICache:
    @property
    def size(self) -> int:
        raise NotImplementedError()

    def destroy(self) -> None:
        raise NotImplementedError()

    def contains(self, param1) -> bool:
        raise NotImplementedError()

    def extract(self, param1) -> Any:
        raise NotImplementedError()

    def peek(self, param1) -> Any:
        raise NotImplementedError()

    def store(self, param1, param2) -> bool:
        raise NotImplementedError()
