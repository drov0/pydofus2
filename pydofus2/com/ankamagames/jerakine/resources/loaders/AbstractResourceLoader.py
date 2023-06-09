from pydofus2.com.ankamagames.berilia.managers.EventsHandler import EventsHandler
from pydofus2.com.ankamagames.jerakine.newCache.ICache import ICache
from pydofus2.com.ankamagames.jerakine.resources.CacheableResource import CacheableResource
from pydofus2.com.ankamagames.jerakine.resources.IResourceObserver import IResourceObserver
from pydofus2.com.ankamagames.jerakine.types.Uri import Uri

class AbstractResourceLoader(IResourceObserver, EventsHandler):

    _log = None
    MEMORY_TEST = {}
    RES_CACHE_PREFIX = "RES_"

    def __init__(self):
        self._cache:ICache = None
        self._completed = False
        self._filesLoaded = 0
        self._filesTotal = 0

    def checkCache(self, uri: Uri) -> bool:
        cr = self.getCachedValue(uri)
        if cr is not None:
            self.dispatchSuccess(uri, cr.resourceType, cr.resource)
            return True
        return False

    def getCachedValue(self, uri: Uri) -> CacheableResource:
        if uri.protocol == "pak" or uri.fileType != "swf" or not uri.subPath:
            resourceUrl = self.RES_CACHE_PREFIX + uri.toSum()
        else:
            resourceUrl = self.RES_CACHE_PREFIX + Uri(uri.path).toSum()
        if self._cache and self._cache.contains(resourceUrl):
            cr = self._cache.peek(resourceUrl)
            return cr
        return None

    def isInCache(self, uri: Uri) -> bool:
        return self.getCachedValue(uri) is not None

    def cancel(self) -> None:
        self._filesTotal = 0
        self._filesLoaded = 0
        self._completed = False
        self._cache = None

    def dispatchSuccess(self, uri: Uri, resourceType: int, resource):
        resourceUrl = None
        cr = None
        rle = None
        rlpe = None

        if uri.fileType != "swf" or not uri.subPath or len(uri.subPath) == 0:
            resourceUrl = self.RES_CACHE_PREFIX + uri.toSum()
        else:
            resourceUrl = self.RES_CACHE_PREFIX + Uri(uri.path).toSum()

        if self._cache and not self._cache.contains(resourceUrl):
            cr = CacheableResource(resourceType, resource)
            self._cache.store(resourceUrl, cr)

        self._filesLoaded += 1
        if self.hasEventListener(ResourceLoadedEvent.LOADED):
            rle = ResourceLoadedEvent(ResourceLoadedEvent.LOADED)
            rle.uri = uri
            rle.resourceType = resourceType
            rle.resource = resource
            self.dispatchEvent(rle)

        if self.hasEventListener(ResourceLoaderProgressEvent.LOADER_PROGRESS):
            rlpe = ResourceLoaderProgressEvent(ResourceLoaderProgressEvent.LOADER_PROGRESS)
            rlpe.uri = uri
            rlpe.filesTotal = self._filesTotal
            rlpe.filesLoaded = self._filesLoaded
            self.dispatchEvent(rlpe)

        if self._filesLoaded == self._filesTotal:
            self.dispatchComplete()

    def dispatchFailure(self, uri: Uri, errorMsg: str, errorCode: int):
        ree = None

        if self._filesTotal == 0:
            return

        self._filesLoaded += 1

        if self.hasEventListener(ResourceErrorEvent.ERROR):
            ree = ResourceErrorEvent(ResourceErrorEvent.ERROR)
            ree.uri = uri
            ree.errorMsg = errorMsg
            ree.errorCode = errorCode
            self.dispatchEvent(ree)
        else:
            self._log.error("[Error code " + str(hex(errorCode)) + "] Unable to load resource " + str(uri) + ": " + errorMsg)

        if self._filesLoaded == self._filesTotal:
            self.dispatchComplete()

    def dispatchComplete(self):
        rlpe = None

        if not self._completed:
            self._completed = True
            rlpe = ResourceLoaderProgressEvent(ResourceLoaderProgressEvent.LOADER_COMPLETE)
            rlpe.filesTotal = self._filesTotal
            rlpe.filesLoaded = self._filesLoaded
            self.dispatchEvent(rlpe)

    def onLoaded(self, uri: Uri, resourceType: int, resource):
        self.MEMORY_TEST[resource] = 1
        self.dispatchSuccess(uri, resourceType, resource)

    def onFailed(self, uri: Uri, errorMsg: str, errorCode: int):
        self.dispatchFailure(uri, errorMsg, errorCode)

    def onProgress(self, uri: Uri, bytesLoaded: int, bytesTotal: int):
        rpe = ResourceProgressEvent(ResourceProgressEvent.PROGRESS)
        rpe.uri = uri
        rpe.bytesLoaded = bytesLoaded
        rpe.bytesTotal = bytesTotal
        self.dispatchEvent(rpe)
