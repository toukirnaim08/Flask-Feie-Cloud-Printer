
## Running locally

Run the following commands to bootstrap your environment if you are unable to run the application using Docker

```bash
cd printing-solution
pip install -r requirements.txt
npm install
npm run-script build
npm start  # run the webpack dev server and flask server using concurrently
```

## Running the Service via Docker

For this you will need to use a comment something like the following. In this case we refer to the config file found in the unido-config repo.

```shell
docker run -p 7095:7095 --env-file ../unido-config/prod/docker/unido-printing-service/env.cfg pacdocker.azurecr.io/unido-printing-service-production:latest
```

## Running Workers Manually

The workers are launched due to the configuration that can be found in supervised_programs/worker*.conf.

To run them in a dev environment, you need to:
* Set FLASK_APP variable: FLASK_APP=autoapp-worker.py
* Run: python3 -m flask rq worker printing-default
  * the queue will typically be printing-default

This will of course not be running it in a debug session. The rq library uses os.fork that is not available on Windows.

### Setting Up Redis

If you don't have redis running locally, you will need to start it up. This can be performed with the following commend:

```
 docker run -d -p 6379:6379 --name redis redis:latest
```

For the worker processes to be able to connect to the above docker Redis instance, they need to bind via:
```
RQ_REDIS_URL=redis://172.17.0.1:6379/0
```
