from typing import List

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.mapper import hierarchy_mapper
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.record.intermediate_structures import IntermediateRow


def fetch_by_project(project_name: str) -> List[IntermediateRow]:
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    result = db.get_collection(project_name).find({})
    return [hierarchy_mapper.to_row(x) for x in result]
