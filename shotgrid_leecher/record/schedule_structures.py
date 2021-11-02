from datetime import datetime
from typing import Optional, Any, Dict

import attr


@attr.s(auto_attribs=True, frozen=True)
class ScheduleLog:
    id: str
    batch_result: str
    project_name: str
    project_id: int
    datetime: datetime
    data: Optional[Dict[str, Any]]

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "ScheduleLog":
        dic: Dict[str, Any] = {
            **{k: v for k, v in raw_dic.items() if k != "_id"},
            "id": str(raw_dic["_id"]),
        }

        return ScheduleLog(
            id=dic["id"],
            project_id=dic["project_id"],
            project_name=dic["project_name"],
            datetime=dic["datetime"],
            batch_result=dic["batch_result"],
            data=dic["data"],
        )


@attr.s(auto_attribs=True, frozen=True)
class ScheduleProject:
    project_id: int
    project_name: str
    datetime: datetime

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "ScheduleProject":
        keys = set(attr.fields_dict(ScheduleProject).keys())
        commands = raw_dic.get("command", dict()).items()
        dic: Dict[str, Any] = {
            **{k: v for k, v in commands if k in keys},
            **{k: v for k, v in raw_dic.items() if k in keys},
        }
        return ScheduleProject(
            project_id=dic["project_id"],
            project_name=dic["project_name"],
            datetime=dic["datetime"],
        )


@attr.s(auto_attribs=True, frozen=True)
class ScheduleQueueItem:
    id: str
    project_name: str
    project_id: int
    datetime: datetime

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "ScheduleQueueItem":
        keys = set(attr.fields_dict(ScheduleQueueItem).keys())
        upper = {"id" if k == "_id" else k: v for k, v in raw_dic.items()}
        commands = raw_dic.get("command", dict()).items()
        dic: Dict[str, Any] = {
            **{k: v for k, v in commands if k in keys},
            **{k: v for k, v in upper.items() if k in keys},
            "id": str(upper["id"]),
        }
        return ScheduleQueueItem(
            id=dic["id"],
            project_name=dic["project_name"],
            project_id=dic["project_id"],
            datetime=dic["datetime"],
        )