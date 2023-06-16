from pydofus2.com.ankamagames.jerakine.resources.adapters.IAdapter import \
    IAdapter
from pydofus2.com.ankamagames.jerakine.resources.IResourceObserver import \
    IResourceObserver
from pydofus2.com.ankamagames.jerakine.resources.ResourceType import \
    ResourceType


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
        with open(path, "rb") as fp:
            self.process(fp.read())
        
    def process(self, image: bytes) -> None:
        self._observer.onLoaded(self._uri, self.getResourceType(), image)
        
    def loadFromData(self, uri, data, observer, dispatchProgress):
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress
        self.process(data)
    
    def getResourceType(self) -> int:
        return ResourceType.RESOURCE_BITMAP
    