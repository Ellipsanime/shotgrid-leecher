import os

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

import shotgrid_leecher.controller.batch_controller as batch
import shotgrid_leecher.controller.schedule_controller as schedule
import shotgrid_leecher.controller.version_controller as version
from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.utils.logger import get_logger

app = FastAPI()
app.include_router(batch.router)
app.include_router(version.router)
app.include_router(schedule.router)

_LOG = get_logger(__name__.split(".")[-1])


@app.on_event("startup")
@repeat_every(seconds=60, logger=_LOG)
async def batch_schedule() -> None:
    await schedule_domain.unroll_batches()


def start():
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("APP_PORT", 9001))


if __name__ == "__main__":
    start()
