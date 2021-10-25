from datetime import datetime
from typing import Optional, Any, Dict

import attr
import cattr


@attr.s(auto_attribs=True, frozen=True)
class ScheduleLog:
    id: str
    batch_result: str
    project_name: str
    project_id: int
    datetime: datetime
    data: Optional[Dict[str, Any]]

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ScheduleLog":
        raw_dic = {"id" if k == "_id" else k: v for k, v in dic.items()}
        return cattr.structure(
            {**raw_dic, "id": str(raw_dic["id"])}, ScheduleLog
        )


@attr.s(auto_attribs=True, frozen=True)
class ScheduleProject:
    project_id: int
    project_name: str
    datetime: datetime

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ScheduleProject":
        keys = set(attr.fields_dict(ScheduleProject).keys())
        commands = dic.get("command", dict()).items()
        raw_dic = {
            **{k: v for k, v in commands if k in keys},
            **{k: v for k, v in dic.items() if k in keys},
        }
        return cattr.structure(raw_dic, ScheduleProject)


@attr.s(auto_attribs=True, frozen=True)
class ScheduleQueueItem:
    id: str
    project_name: str
    project_id: int
    datetime: datetime

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ScheduleQueueItem":
        keys = set(attr.fields_dict(ScheduleQueueItem).keys())
        upper = {"id" if k == "_id" else k: v for k, v in dic.items()}
        commands = dic.get("command", dict()).items()
        raw_dic = {
            **{k: v for k, v in commands if k in keys},
            **{k: v for k, v in upper.items() if k in keys},
        }
        return cattr.structure(
            {**raw_dic, "id": str(raw_dic["id"])}, ScheduleQueueItem
        )
