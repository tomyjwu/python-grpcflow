# python-grpcflow
playground for python grpc to serve Dialogflow fulfillment

## setup
```
python3 -m venv ./env
source env/bin/activate
pip install -r requirements.txt
```
## server
```
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    grpcflow.proto
```

for windows
```
python -m grpc_tools.protoc     -I.     --python_out=.     --grpc_python_out=.     grpcflow.proto
```

start the server:

```bash
export PORT=50061
python server.py
```

for windows
```
set PORT=50061
python server.py
```


Now the server should be listening on port `50061`. We'll use the tool
[`grpcurl`](https://github.com/fullstorydev/grpcurl) to manually interact with it.
On Linux and Mac you can install it with `curl -s https://grpc.io/get_grpcurl | bash`.

```bash
grpcurl \
    -d '{"responseId": "aabbccdd-4096", 
    "session": "project/fujen-smart-iot/agent/sessions/deadbeaf", 
    "queryResult": { 
        "queryText": "your name?", 
        "parameters": {}, 
        "allRequiredParamsPresent": true, 
        "fulfillmentText": "my name is dialogflow", 
        "fulfillmentMessages": {"text": {"text":["my name is dialogflow"]}}, 
        "outputContexts": [{"name":"projects/fujen-smart-iot/agent/sessions/aabbccdd/contexts/__system_counters__"}], 
        "parameters":{"no-input":0,"no-match":0}, 
        "intent": {"name":"projects/fujen-smart-iot/agent/intents/aabbccdd",  "displayName":"get-agent-name"}, 
        "intentDetectionConfidence":1, 
        "languageCode":"zh-tw" 
        } 
    }' \
    --plaintext \
    -proto grpcflow.proto \
    localhost:50061 \
    DialogflowWebhook.fulfillmentWebhook
```

test not handled intents
```bash
grpcurl \
    -d '{"responseId": "aabbccdd-4096", 
    "session": "project/fujen-smart-iot/agent/sessions/deadbeaf", 
    "queryResult": { 
        "queryText": "your name?", 
        "parameters": {}, 
        "allRequiredParamsPresent": true, 
        "fulfillmentText": "my name is dialogflow", 
        "fulfillmentMessages": {"text": {"text":["default name is dialogflow"]}}, 
        "outputContexts": [], 
        "parameters":{}, 
        "intent": {"name":"intents/aabbccdd",  "displayName":"get-my-name"}, 
        "intentDetectionConfidence":1, 
        "languageCode":"zh-tw" 
        } 
    }' \
    --plaintext \
    -proto grpcflow.proto \
    localhost:50061 \
    DialogflowWebhook.fulfillmentWebhook
```

## client
sample node.js client is published as @tomyjwu/grpcflow-client and source code is located in https://github.com/tomyjwu/grpcflow

## container

Now we can build our image. In order to deploy to Cloud Run, we'll be pushing to
the `gcr.io` container registry, so we'll tag it accordingly.

```bash
export GCP_PROJECT=<Your GCP Project Name>
export GCP_PROJECT=fujen-smart-iot
docker build -t gcr.io/$GCP_PROJECT/grpcflow-server:latest .
```

Now, before we deploy to Cloud Run, let's make sure that we've containerized our
application properly. We'll test it by spinning up a local container.

```bash
docker run -d -p 50061:50061 -e PORT=50061 gcr.io/$GCP_PROJECT/grpcflow-server:latest
```

If all goes well, `grpcurl` will give us the same result as before:

```bash
grpcurl \
    -d '{"responseId": "aabbccdd-4096", 
    "session": "project/fujen-smart-iot/agent/sessions/deadbeaf", 
    "queryResult": { 
        "fulfillmentMessages": {"text": {"text":["default name is dialogflow"]}}, 
        "intent": {"name":"intents/aabbccdd",  "displayName":"get-agent-name"}, 
        "languageCode":"zh-tw" 
        } 
    }' \
    --plaintext \
    -proto grpcflow.proto \
    localhost:50061 \
    DialogflowWebhook.fulfillmentWebhook
```

## Deploying to Cloud Run

Cloud Run needs to pull our application from a container registry, so the first
step is to push the image we just built.

Make sure that [you can use `gcloud`](https://cloud.google.com/sdk/gcloud/reference/auth/login)
and are [able to push to `gcr.io`.](https://cloud.google.com/container-registry/docs/pushing-and-pulling)

```bash
gcloud auth login
gcloud auth configure-docker
```

check your active project
```bash
gcloud config get-value project
```

if not correct, please set it by
```bash
gcloud config set project $GCP_PROJECT
```bash

Now we can push our image.

```bash
docker push gcr.io/$GCP_PROJECT/grpcflow-server:latest
```

Finally, we deploy our application to Cloud Run:

```bash
gcloud run deploy --image gcr.io/$GCP_PROJECT/grpcflow-server:latest --platform managed
```

You may be prompted for auth. If so, choose the unauthenticated option.

This command will give you a message like
```
Service [grpcflow-server] revision [grpcflow-server-00001-baw] has been deployed and is serving 100 percent of traffic at https://grpcflow-server-xyspwhk3xq-uc.a.run.app
```

We can now access the gRPC service at
`grpcflow-server-xyspwhk3xq-uc.a.run.app:443`. Go ahead and leave the `https://`
prefix off. Notice that this endpoint is secured with TLS even though the server
we wrote is using a plaintext connection. Cloud Run provides a proxy that
provides TLS for us. We'll account for that in our `grpcurl` invocation by
leaving off the `--plaintext` flag.

```bash
grpcurl \
    -d '{"responseId": "aabbccdd-4096", 
    "session": "project/fujen-smart-iot/agent/sessions/deadbeaf", 
    "queryResult": { 
        "fulfillmentMessages": {"text": {"text":["default name is dialogflow"]}}, 
        "intent": {"name":"intents/aabbccdd",  "displayName":"get-agent-name"}, 
        "languageCode":"zh-tw" 
        } 
    }' \
    -proto grpcflow.proto \
    grpcflow-server-xyspwhk3xq-uc.a.run.app:443 \
    DialogflowWebhook.fulfillmentWebhook
```

And now you've got an auto-scaling  gRPC Dialogflow webhook service!
