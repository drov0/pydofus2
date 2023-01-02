from pydofus2.com.ankamagames.jerakine.pools.Poolable import Poolable
from pydofus2.mx.utils.LinkedListNode import LinkedListNode


class PoolableLinkedListNode(LinkedListNode, Poolable):
    def __init__(self, value=None):
        super().__init__(value)

    def free(self) -> None:
        self.value = None
        self.prev = None
        self.next = None
