import os

import uvicorn as uvicorn
from fastapi import FastAPI

import shotgrid_leecher.controller.batch_controller as batch

app = FastAPI()
app.include_router(batch.router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("APP_PORT", 9001))


if __name__ == "__main__":
    start()
