import os
import pydofus2.com.ankamagames.dofus.Constants as Constants

class BinaryResource:

    @classmethod
    def getBinaries(cls):
        MODULE = cls.__module__.removeprefix("pydofus2.")
        RESOURCE_PATH = os.path.join(Constants.BINARY_DATA_DIR / f"{cls.ID}_{MODULE}_{MODULE}.bin")
        with open(RESOURCE_PATH, "rb") as fp:
            return fp.read()
