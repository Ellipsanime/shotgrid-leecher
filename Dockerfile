FROM flyingjoe/uvicorn-gunicorn-fastapi:python3.7

ENV MODULE_NAME="shotgrid_leecher.main"

RUN apt-get update && apt-get install -y --no-install-recommends iputils-ping git

COPY ./requirements.txt /app/
COPY ./shotgrid_leecher /app/shotgrid_leecher

WORKDIR /app
RUN pip install -r requirements.txt
