from typing import Any


class WeakReference:
    def __init__(self, obj):
        self.dictionary = dict()
        self.dictionary[obj] = None

    @property
    def object(self) -> Any:
        for n in self.dictionary:
            return n
        return None

    def destroy(self) -> None:
        del self.dictionary
        self.dictionary = None
