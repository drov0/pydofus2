import pydofus2.com.ankamagames.dofus.Constants as Constants

class BinaryResource:

    @classmethod
    def getBinaries(cls):
        MODULE = ".".join(cls.__module__.split(".")[1:])
        RESOURCE_PATH = Constants.BINARY_DATA_DIR / f"{cls.ID}_{MODULE}_{MODULE}.bin"
        fp = RESOURCE_PATH.resolve().open("rb")
        return fp.read()
