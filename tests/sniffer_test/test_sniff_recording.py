import os
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from snifferApp.network.sniffer import DofusSniffer


def handle(msg):
    pass


CURRDIR = os.path.dirname(os.path.realpath(__file__))

mySniffer = DofusSniffer(handle)
it = 0
with open(CURRDIR + "/recording.bin", "rb") as fs:
    ba = ByteArray(fs.read())
    while ba.remaining():
        len = ba.readUnsignedInt()
        packet = ba.read(len)
        mySniffer.mockReceiveFromServer(packet)
