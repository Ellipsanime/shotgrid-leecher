from typing import Dict, Any, Union

from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridNode,
    ShotgridRef, ShotgridRefType,
)
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__)


def _dict_to_ref(dic: Dict[str, Any]) -> ShotgridRef:
    if dic.get("kind") == ShotgridRefType.EMPTY.value.lower():
        return ShotgridRef(ShotgridRefType.EMPTY, None)
    if dic.get("kind") == ShotgridRefType.LIST.value.lower():
        return ShotgridRef(ShotgridRefType.LIST, None)
    try:
        val: Union[Dict, Any] = dic.get("value", "")
        if type(val) != dict:
            type_ = ShotgridRefType[val.strip().upper()]
            return ShotgridRef(type_, None)
        type_ = ShotgridRefType[val.get("type").strip().upper()]
        id_ = int(val.get("id"))
        return ShotgridRef(type_, id_)

    except KeyError as error:
        _LOG.warning(error)
        return ShotgridRef(ShotgridRefType.UNKNOWN, None)


def dict_to_shotgrid_node(dic: Dict[str, Any]) -> ShotgridNode:
    ref = _dict_to_ref(dic.get("ref"))
    return ShotgridNode(dic.get("label"), dic.get("path"), ref, [])
