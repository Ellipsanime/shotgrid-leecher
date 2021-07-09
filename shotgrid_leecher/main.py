from typing import Any, Dict

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every


app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=60)
async def leech_events() -> None:
    print("TODO: Leeching shotgrid events !!!!")


@app.get("/events")
async def events(user_id: str) -> Dict[str, Any]:
    return {"id": -1}
