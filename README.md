# shotgrid leecher
Shotgrid application server representing high level abstraction of Shotgrid data model exposed to OpenPype application.

## Run
In order to run a standalone version of the application merely run following command:
```shell
python -m shotgrid_leecher.main
```

## Deploy
Deployment phase based on _gunicorn_ server which is more production-oriented version of WSGI HTTP server than _uvicorn_.

You can find more details about both servers on:

 - https://www.gunicorn.org/
 - https://www.uvicorn.org/

### Docker

 - From the project directory run:
```shell
docker build . -t leecher --no-cache
```
 - Run built image with:
```shell
docker run -e MONGODB_URL='mongodb://127.0.0.1:27017' \
  -e MAX_WORKERS="1" \
  -p 8080:8080 -e PORT="8080" -d --name leecher leecher
```
Here **MONGODB_URL** points to the OpenPype database instance and **PORT** specifies the API leecher server port

 - Once container up and running you must be able to see the documentation on `http://YOUR_HOST:8080/docs`

 - You can use additional environment variables such as:
   - **WORKERS_PER_CORE**
   - **MAX_WORKERS** - **Bugfix** (Must be fixed at 1 for now)
   - **WEB_CONCURRENCY**
   - **LOG_LEVEL**
   - **HOST**
   - [Etc](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) ...


### Docker Swarm mode cluster with Traefik and HTTPS

 - **TODO**
