import math
import random

from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import \
    ThreadSharedSingleton


class InterClientManager(metaclass=ThreadSharedSingleton):
    KEY_SIZE = 21
    hex_chars = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    used_keys = set()

    def __init__(self):
        self.used_keys = set()
        self._numClients = 0

    def getFlashKey(self):
        key = self.get_random_flash_key()
        while key in self.used_keys:
            key = self.get_random_flash_key()
        self.used_keys.add(key)
        nbrKeys = len(self.used_keys)
        suffix = f"#{0 if nbrKeys < 10 else ''}{nbrKeys}"
        self._numClients += 1
        return key + suffix

    @classmethod
    def get_random_flash_key(cls) -> str:
        s_sentence: str = ""
        n_len: int = cls.KEY_SIZE - 4
        for i in range(n_len):
            s_sentence += cls.get_random_char()
        return s_sentence + cls.checksum(s_sentence)

    @classmethod
    def checksum(cls, s: str) -> str:
        r: int = 0
        for i in range(len(s)):
            r += ord(s[i]) % 16
        return cls.hex_chars[r % 16]

    @classmethod
    def get_random_char(cls) -> str:
        n: int = math.ceil(random.random() * 100)
        if n <= 40:
            return chr(math.floor(random.random() * 26) + 65)
        if n <= 80:
            return chr(math.floor(random.random() * 26) + 97)
        return chr(math.floor(random.random() * 10) + 48)

    @property
    def numClients(self):
        return self._numClients

    @numClients.setter
    def numClients(self, value):
        self._numClients = value