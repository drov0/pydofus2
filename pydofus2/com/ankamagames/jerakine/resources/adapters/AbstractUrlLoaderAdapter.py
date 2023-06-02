import abc

import requests


class AbstractUrlLoaderAdapter(metaclass=abc.ABCMeta):

    def __init__(self):
        self._observer = None
        self._uri = None
        self._dispatchProgress = None

    def loadDirectly(self, uri, path, observer, dispatchProgress):
        if self._observer is not None:
            raise Exception("A single adapter can't handle two simultaneous loadings.")
        self._observer = observer
        self._uri = uri
        self._dispatchProgress = dispatchProgress
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

    def process(self, data):
        resource = self.getResource(data)
        self._observer.onLoaded(self._uri, self.getResourceType(), resource)
        self.free()

    @abc.abstractmethod
    def getResource(self, data):
        pass

    @abc.abstractmethod
    def getResourceType(self):
        pass
    
    @abc.abstractmethod
    def dispatchFailure(self, err, code):
        pass
        