import os

import uvicorn as uvicorn

from shotgrid_leecher.setup import setup_all
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])


def start():
    app = setup_all()
    port = int(os.getenv("APP_PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
