import datetime
import os

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every

import controller.batch_controller as batch
import controller.metadata_controller as meta
import controller.schedule_controller as schedule
from const import PROJECT_META
from domain import schedule_domain
from record.commands import CleanScheduleBatchLogsCommand
from utils.logger import get_logger

app = FastAPI(**PROJECT_META)
app.include_router(batch.router)
app.include_router(meta.router)
app.include_router(schedule.router)

origins = [
    "http://localhost",
    "http://localhost:8090",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8090",
    "http://127.0.0.1:3000",
    "http://rnd.ellipsanime.net/",
    "http://rnd.ellipsanime.net:8090/",
    "http://rnd.ellipsanime.net:3000/",
    "http://35.181.15.175",
    "http://35.181.15.175:8090",
    "http://35.181.15.175:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 8090)))


if __name__ == "__main__":
    start()
