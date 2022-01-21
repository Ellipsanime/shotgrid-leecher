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

You might need to install a local docker (registry)[https://hub.docker.com/_/registry] or utilize any centrilized registry prior to any service deployment operation within your swarm.
Step zero is to build the image as followed:
```bash
docker build . -t leecher --no-cache
```

Once your image ready and you opt for a local registry you will need to tag and redeploy the image:
```bash
docker tag shotgrid-leecher localhost:5000/shotgrid-leecher
docker push localhost:5000/shotgrid-leecher
```

Then in order to deploy leecher service as a part of docker swarm stack it's preferable to use an `.env` file.
The deployment command can be as followed:
```bash
env $(cat .env | grep "^[A-Z]" | xargs) docker stack deploy --compose-file docker-compose.yml shotgrid-leecher --resolve-image=never
```
