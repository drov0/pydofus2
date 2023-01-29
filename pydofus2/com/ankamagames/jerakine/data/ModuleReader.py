from collections import OrderedDict
from functools import lru_cache
from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from typing import Any
from pydofus2.com.ankamagames.jerakine.data.GameDataProcess import GameDataProcess
from pydofus2.com.hurlan.crypto.Signature import Signature
from pydofus2.com.ankamagames.jerakine.data.BinaryStream import BinaryStream
from pydofus2.com.ankamagames.jerakine.data.GameDataClassDefinition import (
    GameDataClassDefinition,
)
import threading

lock = threading.Lock()


class InvalidD2OFile(Exception):
    pass


class ModuleReader:
    def __init__(self, stream: BinaryStream, name: str) -> None:
        if not isinstance(stream, BinaryStream):
            stream = BinaryStream(stream, True)
        self._name = name
        self._stream = stream
        self._streamStartIndex = 7
        self._classes = dict[str, GameDataClassDefinition]()
        self._counter = 0
        stream.seek(0)
        string_header = stream.readBytes(3)
        contentOffset = 0
        if string_header != b"D2O":
            if string_header != Signature.ANKAMA_SIGNED_FILE_HEADER:
                raise InvalidD2OFile("Malformated game data file.")
            stream.readShort()
            contentOffset = stream.readInt()
            self._stream.seek(contentOffset, 1)
            self._streamStartIndex = self._stream.position + 7
            string_header = stream.readBytes(3)
            if string_header != b"D2O":
                raise InvalidD2OFile("Malformated game data file.")
        indexesPointer = stream.readInt()
        self._stream.seek(contentOffset + indexesPointer)
        indexesLength = stream.readInt()
        self._indexes = OrderedDict()
        for _ in range(indexesLength // 8):
            key = stream.readInt()
            pointer = stream.readInt()
            self._indexes[key] = contentOffset + pointer
            self._counter += 1
        classesCount = stream.readInt()
        for _ in range(classesCount):
            classId = stream.readInt()
            self.__readClassDefinition(classId, stream)
        if stream.remaining():
            self._gameDataProcessor = GameDataProcess(stream)

    def clearObjectsCache(self):
        Logger().info(f"[Modulee {self._name}] Clearing objects cache.")
        self.getObjects.cache_clear()

    @lru_cache(maxsize=32, typed=False)
    def getObjects(self):
        with lock:
            if not self._counter:
                return None
            self._stream.seek(self._streamStartIndex)
            objects = list()
            for _ in range(self._counter):
                classId = self._stream.readInt()
                instance = self._classes[classId].from_stream(self._stream)
                objects.append(instance)
            self.getObjects.cache_clear()
            BenchmarkTimer(60, self.clearObjectsCache).start()
            return objects

    def __readClassDefinition(self, classId, stream: BinaryStream):
        className = stream.readUTF()
        packageName = stream.readUTF()
        classDef = GameDataClassDefinition(packageName, className, self)
        fieldsCount = stream.readInt()
        for _ in range(fieldsCount):
            field = stream.readUTF()
            classDef.addField(field, stream)
        self._classes[classId] = classDef

    def getClassDefinition(self, object_id: int) -> GameDataClassDefinition:
        return self._classes[object_id]

    @lru_cache(maxsize=200, typed=False)
    def getObject(self, objectId: int) -> Any:
        with lock:
            if not self._indexes:
                Logger().warning(f"[Module {self._name}] No indexes found in the D2O file")
                return None
            pointer = self._indexes.get(objectId)
            if pointer is None:
                Logger().warning(f"[Module {self._name}] No object found with id {objectId}")
                return None
            self._stream.seek(pointer)
            classId: int = self._stream.readInt()
            BenchmarkTimer(60, self.getObject.cache_clear).start()
            return self._classes[classId].from_stream(self._stream)

    def close(self) -> None:
        for stream in self._streams:
            try:
                if isinstance(stream, BinaryStream):
                    stream.close()
            except Exception as e:
                continue
        self._streams = None
        self._indexes = None
        self._classes = None
