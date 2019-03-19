import os
import logging
import base64

from marshmallow.exceptions import ValidationError
from azure.storage import CloudStorageAccount
import azure.functions as func

from . import put_schema


def encode_message(msg):
    try:
        # ensure bytes
        msg = msg.encode('utf-8')
    except AttributeError:
        pass
    return base64.b64encode(msg).decode('utf-8')


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP Submit trigger received a request')

    logging.debug('Creating blob service')
    account = CloudStorageAccount(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )

    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Post"
    }
    queue_service = account.create_queue_service()
    schema = put_schema.DoneSchema()
    try:
        done_dict = schema.loads(req.get_body())
    except ValidationError:
        error = f'Failed to validate the done message'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )

    done_queue_name = os.getenv('AZURE_DONE_QUEUE_NAME')

    message = schema.dumps(done_dict)
    queue_service.put_message(
        queue_name=done_queue_name,
        content=encode_message(message),
        time_to_live=604800
    )
    return func.HttpResponse('Message was successfully inserted into Done queue',
                             headers=headers_dict,
                             )
