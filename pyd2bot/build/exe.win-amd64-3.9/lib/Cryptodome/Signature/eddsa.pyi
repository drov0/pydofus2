from typing import Union, Optional
from typing_extensions import Protocol
from Cryptodome.PublicKey.ECC import EccKey

class Hash(Protocol):
    def digest(self) -> bytes: ...

class XOF(Protocol):
    def read(self, len: int) -> bytes: ...

def import_public_key(encoded: bytes) -> EccKey: ...
def import_private_key(encoded: bytes) -> EccKey: ...

class EdDSASigScheme(object):

    def __init__(self, key: EccKey, context: bytes) -> None: ...
    def can_sign(self) -> bool: ...
    def sign(self, msg_or_hash: Union[bytes, Hash, XOF]) -> bytes: ...
    def verify(self, msg_or_hash: Union[bytes, Hash, XOF], signature: bytes) -> None: ...

def new(key: EccKey, mode: bytes, context: Optional[bytes]=None) -> EdDSASigScheme: ...