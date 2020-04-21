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

start the server:

```bash
export PORT=50061
python server.py
```

Now the server should be listening on port `50051`. We'll use the tool
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
    DialogflowWebhook.FulfillmentWebhook
```
# usage
todo...
