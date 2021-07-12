import event_leecher as event_leecher
from typing import Any, Dict, NoReturn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every


app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=60)
async def start_leeching_events() -> NoReturn:
    await event_leecher.leech_recent_events()


@app.get("/events")
async def events(user_id: str) -> Dict[str, Any]:
    return {"id": -1}
