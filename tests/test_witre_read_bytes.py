from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

N = 4435
ba = ByteArray()
ba.writeUnsignedInt(N)
ba.writeUTF("ababa")

ba.position = 0
with open("dst.bin", "wb") as f:
    f.write(ba)

with open("dst.bin", "rb") as f:
    ba = ByteArray(f.read())
    ba.position = 0
    r = ba.readUnsignedInt()
    stri = ba.readUTF()
    print(r)
    print(stri)
    assert r == N
