import shotgrid_leecher.utils.connectivity as conn


def _get_avalon_database():
    return conn.get_db_client().get_database("avalon")


def get_project_entity(project_name: str):
    db = _get_avalon_database()
    return db.get_collection(project_name).find_one({"type": "project"})
