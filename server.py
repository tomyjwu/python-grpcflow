import logging
import os
from concurrent import futures

from typing import Text

import grpcflow_pb2
import grpcflow_pb2_grpc

import grpc

_PORT = os.environ["PORT"]

class DialogflowWebhook(grpcflow_pb2_grpc.DialogflowWebhookServicer):

    def get_agenet_name(self, queryResult: grpcflow_pb2.QueryResult) -> grpcflow_pb2.DialogflowWebhookResponse:
        textObj = grpcflow_pb2.FulfillmentMessage.FulfillmentText(text=["my name is grpcflow"])
        textResponse = grpcflow_pb2.FulfillmentMessage(text=textObj)
        response = grpcflow_pb2.DialogflowWebhookResponse(fulfillmentMessages=textResponse)
        return response

    def FulfillmentWebhook(self,
            request: grpcflow_pb2.DialogflowWebhookRequest,
            context: grpc.ServicerContext) -> grpcflow_pb2.DialogflowWebhookResponse:
        logging.info("Received request: %s", request)
        intentDisplayName = request.queryResult.intent.displayName
        if intentDisplayName == "get-agent-name":
            res = self.get_agenet_name(request.queryResult)
        # elif x==y:
        else:
            logging.error("unexpected intent")
            # return original message
            res = grpcflow_pb2.DialogflowWebhookResponse()
            res.fulfillmentMessages.CopyFrom(request.queryResult.fulfillmentMessages)

        return res


def _serve(port: Text):
    bind_address = f"[::]:{port}"
    server = grpc.server(futures.ThreadPoolExecutor())
    grpcflow_pb2_grpc.add_DialogflowWebhookServicer_to_server(DialogflowWebhook(), server)
    server.add_insecure_port(bind_address)
    server.start()
    logging.info("Listening on %s.", bind_address)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _serve(_PORT)
