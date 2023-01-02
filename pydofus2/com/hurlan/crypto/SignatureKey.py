from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from Cryptodome.PublicKey import RSA


class SignatureKey(RSA.RsaKey):
    PUBLIC_KEY_HEADER: str = "DofusPublicKey"
    PRIVATE_KEY_HEADER: str = "DofusPrivateKey"

    def __init__(self, *args, **kwargs: int) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def import_key(cls, input: ByteArray) -> "SignatureKey":
        header: str = input.readUTF()
        if (
            header != SignatureKey.PUBLIC_KEY_HEADER
            and header != SignatureKey.PRIVATE_KEY_HEADER
        ):
            raise Exception("Invalid public or private header")
        if header == SignatureKey.PUBLIC_KEY_HEADER:
            N = input.readUTF()
            N = int.from_bytes(bytes(N, "utf"), "big")
            E = input.readUTF()
            E = int.from_bytes(bytes(E, "utf"), "big")
            return SignatureKey(n=N, e=E)
