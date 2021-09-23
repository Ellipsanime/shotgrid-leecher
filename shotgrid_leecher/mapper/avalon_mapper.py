from typing import Dict, Any, List

Map = Dict[str, Any]


def entity_to_project(source_entity: Map, hierarchy_rows: List[Map]) -> Map:
    shotgrid_project = [
        item for item in hierarchy_rows if item["type"] == "Project"
    ][-1]

    if source_entity and shotgrid_project:
        return {
            "_id": shotgrid_project["_id"],
            "src_id": shotgrid_project["src_id"],
            "object_id": source_entity["_id"],
            "type": "Project",
            "parent": None,
        }
    return {}
