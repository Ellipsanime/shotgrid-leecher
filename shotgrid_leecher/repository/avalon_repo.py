from typing import Dict, Any

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import DbName, ShotgridType


def _get_avalon_database():
    return conn.get_db_client().get_database(DbName.AVALON.value)


def get_project_entity(project_name: str) -> Dict[str, Any]:
    db = _get_avalon_database()
    return db.get_collection(project_name).find_one(
        {"type": ShotgridType.PROJECT.value.lower()}
    )
