import datetime

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from starlette.middleware.cors import CORSMiddleware
from toolz import memoize, compose

from shotgrid_leecher.const import PROJECT_META
from shotgrid_leecher.controller import (
    batch_controller as batch,
    metadata_controller as meta,
    schedule_controller as schedule,
    config_controller as config,
    user_controller as user,
)
from shotgrid_leecher.domain import schedule_domain, user_domain
from shotgrid_leecher.record.commands import CleanScheduleBatchLogsCommand
from shotgrid_leecher.utils.logger import get_logger

_START_EVENT = "startup"
_LOG = get_logger(__name__.split(".")[-1])


def setup_cors(app: FastAPI) -> FastAPI:
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "https://rnd.ellipsanime.net:443",
        "http://rnd.ellipsanime.net:9010",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


@memoize
def setup_app() -> FastAPI:
    app = FastAPI(**PROJECT_META)
    app.include_router(batch.router)
    app.include_router(meta.router)
    app.include_router(schedule.router)
    app.include_router(config.router)
    app.include_router(user.router)
    return app


def setup_events(app: FastAPI) -> FastAPI:

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

    @app.on_event("startup")
    @repeat_every(seconds=60 * 2, logger=_LOG)
    async def synchronize_links() -> None:
        await user_domain.synchronize_project_user_links()

    return app


setup_all = compose(setup_events, setup_cors, setup_app)
