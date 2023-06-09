from pydofus2.com.ankamagames.jerakine.resources.loaders.ResourceLoaderType import ResourceLoaderType
from pydofus2.com.ankamagames.jerakine.resources.loaders.impl.SingleResourceLoader import SingleRessourceLoader


class ResourceLoaderFactory:
    @staticmethod
    def getLoader(type):
        if type == ResourceLoaderType.PARALLEL_LOADER:
            return ParallelRessourceLoader(JerakineConstants.MAX_PARALLEL_LOADINGS)
        elif type == ResourceLoaderType.SERIAL_LOADER:
            return ParallelRessourceLoader(1)
        elif type == ResourceLoaderType.SINGLE_LOADER:
            return SingleRessourceLoader()
        else:
            raise ValueError("Unknown loader type " + str(type) + ".")
