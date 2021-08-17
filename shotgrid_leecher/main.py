from typing import Any, Dict

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from shotgrid_leecher import event_leecher

app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=60)
async def start_leeching_events() -> None:
    event_leecher.get_recent_events()
    # asset_events_service.get_recent_events()


@app.get("/events")
async def events(user_id: str) -> Dict[str, Any]:
    return {"id": -1}


def start():
    uvicorn.run(app, host="0.0.0.0", port=9001)


if __name__ == "__main__":
    event_leecher.get_recent_events()
    start()
