import shotgrid_leecher.utils.connectivity as conn


def get_last_rows(project_name: str):
    db = conn.get_db_client().get_database("shotgrid_openpype")
    return db.get_collection(project_name).find({})
