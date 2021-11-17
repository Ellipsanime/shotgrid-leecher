from typing import List

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.mapper import hierarchy_mapper
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateRow,
    IntermediateParams,
)


def fetch_by_project(
    project_name: str,
    project_params: IntermediateParams,
) -> List[IntermediateRow]:
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    result = db.get_collection(project_name).find({})
    return [hierarchy_mapper.to_row(x, project_params) for x in result]
