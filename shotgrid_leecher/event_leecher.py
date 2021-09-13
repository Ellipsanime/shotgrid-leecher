from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.repository import shotgrid_hierarchy_repo


def get_recent_events() -> None:
    project_rows = shotgrid_hierarchy_repo.get_hierarchy_by_project(209)
    batch_domain.batch_shotgrid_to_avalon(ShotgridToAvalonBatchCommand(209, True))
    print(project_rows)
    pass
