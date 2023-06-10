import io
from typing import Any
from PIL import Image
from pydofus2.com.ankamagames.jerakine.resources.IResourceObserver import IResourceObserver

from pydofus2.com.ankamagames.jerakine.resources.ResourceType import ResourceType
from pydofus2.com.ankamagames.jerakine.resources.adapters.IAdapter import IAdapter

class BitmapAdapter(IAdapter):
    
    def __init__(self):
        self._observer = None
        self._uri = None
        self._dispatchProgress = None
    
    def loadDirectly(self, uri: str, path: str, observer: IResourceObserver, dispatchProgress: bool) -> None:
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress
        image = Image.open(path)
        self.process(image)
        
    def process(self, image: Image) -> None:
        self._observer.onLoaded(self._uri, self.getResourceType(), image)
        
    def loadFromData(self, uri, data, observer, dispatchProgress):
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress
        image = Image.open(io.BytesIO(data))
        self.process(image)
    
    def getResourceType(self) -> int:
        return ResourceType.RESOURCE_BITMAP
    