from Cryptodome.PublicKey import RSA as RSA

from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import \
    ByteArray
from pydofus2.com.hurlan.crypto.symmetric.IPad import IPad


class RSACipher:
    def __init__(self, key: RSA.RsaKey, padding: IPad) -> None:
        self.key = key
        self.padding = padding
        self.blockSize = (self.key.n.bit_length() + 7) // 8
        self.padding.setBlockSize(self.blockSize)

    def verify(self, src: ByteArray, out: ByteArray) -> bool:
        out.position = 0
        for i in range(0, len(src), self.blockSize):
            block = int.from_bytes(src[i : i + self.blockSize], "big", signed=False)
            chunk = pow(block, self.key.e, self.key.n)
            b = chunk.to_bytes(self.blockSize, "big", signed=False)
            plain_text_block = self.padding.unpad(b, 1)
            if not plain_text_block:
                Logger().error("Decrypt error - padding function returned None!")
                return False
            out.writeByteArray(plain_text_block)
        out.position = 0
        return True

    def encrypt(self, src: ByteArray) -> ByteArray:
        out = ByteArray()
        for i in range(0, len(src), self.blockSize):
            block = int.from_bytes(self.padding.pad(src[i : i + self.blockSize]), "big", signed=False)
            cypher_chunk_base10 = pow(block, self.key.e, self.key.n)
            cypher_chunk_bytes = cypher_chunk_base10.to_bytes(self.blockSize, "big", signed=False)
            out.writeByteArray(cypher_chunk_bytes)
        out.position = 0
        return out

    def decrypt(self, src: ByteArray) -> ByteArray:
        if not self.key.has_private():
            Logger().error("Decrypt error - RSA key does not have a private part!")
            return None
        out = ByteArray()
        for i in range(0, len(src), self.blockSize):
            block = int.from_bytes(src[i : i + self.blockSize], "big", signed=False)
            chunk = pow(block, self.key.d, self.key.n)
            b = chunk.to_bytes(self.blockSize, "big", signed=False)
            plain_text_block = self.padding.unpad(b, 1)
            if not plain_text_block:
                Logger().error("Decrypt error - padding function returned None!")
                return None
            out.writeByteArray(plain_text_block)
        out.position = 0
        return out
