import abc

import requests

from pydofus2.com.ankamagames.jerakine.resources.IResourceObserver import IResourceObserver
from pydofus2.com.ankamagames.jerakine.types.Uri import Uri


class AbstractUrlLoaderAdapter(metaclass=abc.ABCMeta):

    def __init__(self):
        self._observer = None
        self._uri = None
        self._dispatchProgress = None

    def loadDirectly(self, uri: Uri, path, observer:IResourceObserver, dispatchProgress):
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress

        if uri.protocol == "file":
            with open(path, "rb") as file:
                self.process("BINARY", file.read())
        else:
            response = requests.get(path)
            self.process(response.content)
            
    def loadFromData(self, uri, data, observer, dispatchProgress):
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress
        self.process(data)

    def free(self):
        self._observer = None
        self._uri = None

    def process(self, dataFormat:str, data):
        resource = self.getResource(dataFormat, data)
        self._observer.onLoaded(self._uri, self.getResourceType(), resource)
        self.free()

    def getResource(self, dataFormat:str, data):
        pass

    def getResourceType(self):
        pass
    
    def dispatchFailure(self, err, code):
        pass
        