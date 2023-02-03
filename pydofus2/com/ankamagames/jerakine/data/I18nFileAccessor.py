from functools import lru_cache
import threading
from time import perf_counter
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import MemoryProfiler
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton
from pydofus2.com.ankamagames.jerakine.data.BinaryStream import BinaryStream


class I18nFileAccessor(metaclass=ThreadSharedSingleton):

    _initialized = threading.Event()
    _initializing = threading.Event()

    def __init__(self) -> None:
        self.directBuffer = None
        if I18nFileAccessor._initialized.is_set():
            Logger().info("I18n file already loaded.")
            return
        if I18nFileAccessor._initializing.is_set():
            Logger().info("I18n file is already loading.")
            I18nFileAccessor._initialized.wait()
            return
        self.initI18n()
        
    @MemoryProfiler.track_memory("I18nFileAccessor.init")
    def initI18n(self):
        self._initializing.set()
        Logger().info("Loading I18n file...")
        s = perf_counter()
        with open(Constants.LANG_FILE_PATH, "rb") as fp:
            stream = BinaryStream(fp, big_endian=True)
            self.indexes = dict()
            self.unDiacriticalIndex = dict()
            self.textIndexes = dict()
            self.textIndexesOverride = dict()
            self.textSortIndex = dict()
            self.textCount = 0
            indexesPointer: int = stream.readInt()
            keyCount: int = 0
            stream.position = indexesPointer
            indexesLength: int = stream.readInt()
            i = 0
            while i < indexesLength:
                key = stream.readInt()
                diacriticalText = stream.readbool()
                pointer = stream.readInt()
                i += 9
                self.indexes[key] = pointer
                keyCount += 1
                if diacriticalText:
                    keyCount += 1
                    i += 4
                    self.unDiacriticalIndex[key] = stream.readInt()
                else:
                    self.unDiacriticalIndex[key] = pointer
            indexesLength = stream.readInt()
            while indexesLength > 0:
                position = stream.position
                textKey = stream.readUTF()
                pointer = stream.readInt()
                self.textCount += 1
                self.textIndexes[textKey] = pointer
                indexesLength -= stream.position - position
            indexesLength = stream.readInt()
            i = 0
            while indexesLength > 0:
                position = stream.position
                i += 1
                self.textSortIndex[stream.readInt()] = i
                indexesLength -= stream.position - position
            textKeys: list = []
            for textKey in self.textIndexes:
                textKeys.append(textKey)
        self._initializing.clear()
        self._initialized.set()
        Logger().info(f"Loaded {keyCount} keys and {self.textCount} texts. in {perf_counter() - s}s")

    def logInit() -> None:
        Logger().debug("Initialized !")

    def setEntries(self, textKey: str) -> None:
        LangManager().setEntry(textKey, self.getNamedText(textKey))

    def overrideId(self, oldId: int, newId: int) -> None:
        self.indexes[oldId] = self.indexes[newId]
        self.unDiacriticalIndex[oldId] = self.unDiacriticalIndex[newId]

    def getOrderIndex(self, key: int) -> int:
        return self.textSortIndex[key]

    @lru_cache(maxsize=128)
    def getText(self, key: int) -> str:
        if not self.indexes:
            return None
        pointer = self.indexes.get(key)
        if not pointer:
            return None
        if self.directBuffer is None:
            with open(Constants.LANG_FILE_PATH, "rb") as fp:
                stream = BinaryStream(fp, big_endian=True)        
                stream.position = pointer
                return stream.readUTF()
        self.directBuffer.position = pointer
        return self.directBuffer.readUTF()
    
    @lru_cache(maxsize=128)
    def getUnDiacriticalText(self, key: int) -> str:
        if not self.unDiacriticalIndex:
            return None
        pointer: int = self.unDiacriticalIndex.get(key)
        if not pointer:
            return None
        with open(Constants.LANG_FILE_PATH, "rb") as fp:
            stream = BinaryStream(fp, big_endian=True)
            if self.directBuffer is None:
                stream.position = pointer
                return stream.readUTF()
        self.directBuffer.position = pointer
        return self.directBuffer.readUTF()

    def hasText(self, key: int) -> bool:
        return self.indexes and key in self.indexes

    @lru_cache(maxsize=128)
    def getNamedText(self, textKey: str) -> str:
        if not self.textIndexes:
            return None
        if textKey in self.textIndexesOverride:
            textKey = self.textIndexesOverride[textKey]
        pointer = self.textIndexes.get(textKey)
        if not pointer:
            return None
        with open(Constants.LANG_FILE_PATH, "rb") as fp:
            stream = BinaryStream(fp, big_endian=True)
            stream.position = pointer
            return stream.readUTF()

    def hasNamedText(self, textKey: str) -> bool:
        return self.textIndexes and self.textIndexes[textKey]

    def useDirectBuffer(self, bool: bool) -> None:
        if self.directBuffer == bool:
            return
        if not bool:
            self.directBuffer = None
        else:
            self.directBuffer = BinaryStream()
            with open(Constants.LANG_FILE_PATH, "rb") as fp:
                stream = BinaryStream(fp, big_endian=True)
                stream.position = 0
                self.directBuffer.writeBytes(stream.readBytes())

    def close(self) -> None:
        self.indexes.clear()
        self.textIndexes.clear()
        self.directBuffer.close()
