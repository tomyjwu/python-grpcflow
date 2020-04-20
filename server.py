import logging
import os
from concurrent import futures

from typing import Text

import grpcflow_pb2
import grpcflow_pb2_grpc

import grpc

_PORT = os.environ["PORT"]

class DialogflowWebhook(grpcflow_pb2_grpc.DialogflowWebhookServicer):

    def FulfillmentWebhook(self,
            request: grpcflow_pb2.DialogflowWebhookRequest,
            context: grpc.ServicerContext) -> grpcflow_pb2.DialogflowWebhookResponse:
        logging.info("Received request: %s", request)
        response = grpcflow_pb2.DialogflowWebhookResponse()
        return response


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