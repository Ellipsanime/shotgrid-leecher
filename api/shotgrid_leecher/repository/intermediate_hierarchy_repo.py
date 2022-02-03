from typing import List

import utils.connectivity as conn
from mapper import intermediate_mapper
from record.enums import DbName
from record.intermediate_structures import (
    IntermediateRow,
    IntermediateParams,
)


def fetch_by_project(
    project_name: str,
    project_params: IntermediateParams,
) -> List[IntermediateRow]:
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    result = db.get_collection(project_name).find({})
    return [intermediate_mapper.to_row(x, project_params) for x in result]
