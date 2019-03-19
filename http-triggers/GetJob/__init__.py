import os
import logging
import base64
import binascii

from marshmallow.exceptions import ValidationError
from azure.storage import CloudStorageAccount
import azure.functions as func

from . import getjob_schema


def decode_message(queue_message):
    try:
        msg = base64.b64decode(queue_message.content).decode('utf-8')
    except binascii.Error:
        msg = queue_message.content
    return msg


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP Submit trigger received a request')

    logging.debug('Creating blob service')
    account = CloudStorageAccount(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )
    queue_service = account.create_queue_service()

    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Post"
    }
    schema = getjob_schema.GetJobSchema()
    try:
        getjob_dict = schema.loads(req.get_body())
    except ValidationError:
        return func.HttpResponse(f'Failed to validate getjob schema',
                                 headers=headers_dict,
                                 status_code=400
                                 )
    if not getjob_dict['num_messages'] == 1:
        return func.HttpResponse(f'Number of messages should be 1',
                                 headers=headers_dict,
                                 status_code=400
                                 )
    await_queue_name = os.getenv('AZURE_AWAIT_QUEUE_NAME')

    message_list = queue_service.get_messages(
        queue_name=await_queue_name
    )
    if len(message_list) == 0:
        return func.HttpResponse(f'No message found',
                                 headers=headers_dict,
                                 status_code=400
                                 )

    message = message_list[0]
    queue_service.delete_message(await_queue_name,
                                 message.id,
                                 message.pop_receipt
                                 )
    return func.HttpResponse(decode_message(message),
                             headers=headers_dict,
                             mimetype='application/json'
                             )
