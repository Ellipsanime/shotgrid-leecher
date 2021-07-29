import os

from toolz import memoize
import shotgun_api3 as sg


@memoize
def _get_shotgrid_connection() -> sg.Shotgun:
    url = os.getenv("SHOTGRID_URL")
    login = os.getenv("SHOTGRID_LOGIN")
    password = os.getenv("SHOTGRID_PASSWORD")
    return sg.Shotgun(url, login=login, password=password)


async def get_recent_events() -> None:
    connection = _get_shotgrid_connection()
    filters = [
        ["id", "greater_than", 100],
        ["event_type", "is", "Shotgun_Asset_New"],
    ]
    fields = [
        "id",
        "event_type",
        "attribute_name",
        "meta",
        "entity",
        "user",
        "project",
        "session_uuid",
        "created_at",
    ]
    order = [{"column": "id", "direction": "asc"}]
    events = connection.find(
        "EventLogEntry",
        filters,
        fields,
        order,
        limit=100,
    )
    print(events)
    pass
