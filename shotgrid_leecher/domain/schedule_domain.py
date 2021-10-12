from shotgrid_leecher.record.commands import ScheduleShotgridBatchCommand
from shotgrid_leecher.writers import schedule_writer as writer


def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    writer.request_scheduling(command)
