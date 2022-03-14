import hashlib
from typing import Any

from bson import ObjectId

_OBJ_ID_LEN = 12


def to_object_id(id_: Any) -> ObjectId:
    return ObjectId(str(id_).zfill(_OBJ_ID_LEN)[:_OBJ_ID_LEN].encode("utf-8"))


def to_sha256_id(source: str) -> str:
    checksum = hashlib.sha256()
    checksum.update(source.encode("utf-8"))
    return str(checksum.hexdigest())
