import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import DbName


def fetch_by_project(project_name: str):
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    return db.get_collection(project_name).find({})
