from pydofus2.flash.net.SharedObject import SharedObject
from pydofus2.mx.utils.UIDUtil import UIDUtil


class DeviceUtils:

    @staticmethod
    def deviceUniqueIdentifier():
        soUid = SharedObject.getLocal("device_uid")
        if not UIDUtil.isUID(soUid.data.uid):
            soUid.data.uid = UIDUtil.createUID()
            soUid.flush()
        return soUid.data.uid
