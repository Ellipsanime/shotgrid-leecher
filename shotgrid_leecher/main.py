import datetime
import os

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

import shotgrid_leecher.controller.batch_controller as batch
import shotgrid_leecher.controller.metadata_controller as meta
import shotgrid_leecher.controller.schedule_controller as schedule
from shotgrid_leecher.const import PROJECT_META
from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.record.commands import CleanScheduleBatchLogsCommand
from shotgrid_leecher.utils.logger import get_logger

app = FastAPI(**PROJECT_META)
app.include_router(batch.router)
app.include_router(meta.router)
app.include_router(schedule.router)

_LOG = get_logger(__name__.split(".")[-1])


@app.on_event("startup")
@repeat_every(seconds=180, logger=_LOG)
async def queue_scheduled_batches() -> None:
    await schedule_domain.queue_scheduled_batches()


@app.on_event("startup")
@repeat_every(seconds=120, logger=_LOG)
async def dequeue_and_process_batches() -> None:
    await schedule_domain.dequeue_and_process_batches()


@app.on_event("startup")
@repeat_every(seconds=60 * 60, logger=_LOG)
async def clean_up_schedule() -> None:
    time_delta = datetime.timedelta(days=14)
    await schedule_domain.schedule_clean_batch_log(
        CleanScheduleBatchLogsCommand(datetime.datetime.now() - time_delta),
    )


def start():
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 9001)))


if __name__ == "__main__":
    start()
