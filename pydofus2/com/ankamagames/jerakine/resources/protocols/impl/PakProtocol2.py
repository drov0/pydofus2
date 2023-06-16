import os
from collections import defaultdict
from io import BufferedReader
from pathlib import Path
from typing import Dict, Optional, Union

from pydofus2.com.ankamagames.jerakine.data.BinaryStream import BinaryStream
from pydofus2.com.ankamagames.jerakine.newCache.ICache import ICache
from pydofus2.com.ankamagames.jerakine.resources.IResourceObserver import \
    IResourceObserver
from pydofus2.com.ankamagames.jerakine.resources.protocols.AbstractProtocol import \
    AbstractProtocol
from pydofus2.com.ankamagames.jerakine.types.Uri import Uri


class PakProtocol2(AbstractProtocol):

    _indexes = defaultdict(dict)
    _properties = defaultdict(dict)

    def __init__(self):
        super().__init__()

    def getFilesIndex(self, uri: Uri) -> Dict:
        fileStream = self._indexes.get(uri.path, None)
        if not fileStream:
            fileStream = self.initStream(uri)
            if not fileStream:
                return None
        return self._indexes[uri.path]

    def loadDirectly(self, uri: Uri) -> bytes:
        index = None
        data = bytearray()
        fileStream = None
        if not self._indexes.get(uri.path):
            fileStream = self.initStream(uri)
            if not fileStream:
                return
        index = self._indexes[uri.path].get(uri.subPath)
        if not index:
            return
        fileStream: BinaryStream = index['stream']
        fileStream.seek(index['o'])
        return fileStream.readBytes(index['l'])
        
    def load(self, uri: Uri, observer: 'IResourceObserver', dispatchProgress: bool, cache: 'ICache', forcedAdapter: 'type', uniqueFile: bool) -> None:
        index = None
        data = bytearray()
        fileStream = None
        if not self._indexes.get(uri.path):
            fileStream = self.initStream(uri)
            if not fileStream:
                if observer:
                    observer.onFailed(uri, "UnableVisible to find container.", 'PAK_NOT_FOUND')
                return
        index = self._indexes[uri.path].get(uri.subPath)
        if not index:
            if observer:
                observer.onFailed(uri, "UnableVisible to find the file in the container.", 'FILE_NOT_FOUND_IN_PAK')
            return
        fileStream: BinaryStream = index['stream']
        fileStream.seek(index['o'])
        data = fileStream.readBytes(index['l'])
        self.getAdapter(uri, forcedAdapter)
        try:
            self._adapter.loadFromData(uri, data, observer, dispatchProgress)
        except Exception as e:
            print(e)
            observer.onFailed(uri, "Can't load byte array from this adapter.", 'INCOMPATIBLE_ADAPTER')
            return

    def initStream(self, uri: Uri) -> 'BufferedReader':
        vMax = 0
        vMin = 0
        dataOffset = 0
        dataCount = 0
        indexOffset = 0
        indexCount = 0
        propertiesOffset = 0
        propertiesCount = 0
        propertyName = None
        propertyValue = None
        filePath = None
        fileOffset = 0
        fileLength = 0
        idx = 0
        fileUri = uri
        # Replace `Path` with the correct method for getting a `Path` object in your environment
        file = Path(fileUri.toFile())
        if not file.exists():
            raise FileNotFoundError(file)
        indexes = defaultdict(dict)
        properties = defaultdict(dict)
        self._indexes[uri.path] = indexes
        self._properties[uri.path] = properties
        while file and file.exists():
            fs = BinaryStream(file.open('rb'), True)
            vMax = fs.readUnsignedByte()
            vMin = fs.readUnsignedByte()
            if vMax != 2 or vMin != 1:
                return None
            fs.seek(-24, os.SEEK_END)
            dataOffset = fs.readUnsignedInt()
            dataCount = fs.readUnsignedInt()
            indexOffset = fs.readUnsignedInt()
            indexCount = fs.readUnsignedInt()
            propertiesOffset = fs.readUnsignedInt()
            propertiesCount = fs.readUnsignedInt()
            fs.position = propertiesOffset
            file = None
            for _ in range(propertiesCount):
                propertyName = fs.readUTF()
                propertyValue = fs.readUTF()
                properties[propertyName] = propertyValue
                if propertyName == "link":
                    file = fileUri.toFile().parent / propertyValue
            fs.seek(indexOffset)
            for _ in range(indexCount):
                filePath = fs.readUTF()
                fileOffset = fs.readUnsignedInt()
                fileLength = fs.readUnsignedInt()
                indexes[filePath] = {
                    "o": fileOffset + dataOffset,
                    "l": fileLength,
                    "stream": fs
                }
        return fs

    def release(self):
        pass