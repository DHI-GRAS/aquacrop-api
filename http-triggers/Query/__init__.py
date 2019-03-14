import os
import logging
import binascii
import base64
import uuid

from azure.storage import CloudStorageAccount
import azure.functions as func

from . import query_schema


def decode_message(queue_message):
    try:
        msg = base64.b64decode(queue_message.content).decode('utf-8')
    except binascii.Error:
        msg = queue_message.content
    return msg


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP Query trigger received a request')

    logging.debug('Creating blob service')
    account = CloudStorageAccount(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )
    queue_service = account.create_queue_service()

    guid = req.params.get('guid')
    if not guid:
        error = f'Check Url paramaters. No guid variable was found'
        return func.HttpResponse(error, status_code=400)
    guid = uuid.UUID(guid)
    logging.info("Creating Dicts")
    await_queue_name = os.getenv('AZURE_AWAIT_QUEUE_NAME')
    done_queue_name = os.getenv('AZURE_DONE_QUEUE_NAME')
    query_response_dict = {}
    query_response_schema = query_schema.QueryResponseSchema()

    logging.info("Searching in await-processing queue")
    messages_awaiting = queue_service.peek_messages(
        await_queue_name,
        num_messages=32
    )
    await_schema = query_schema.AwaitSchema()
    for m in messages_awaiting:
        message_guid = await_schema.loads(decode_message(m))['guid']
        if message_guid == guid:
            query_response_dict['status'] = f'awaiting'
            query_response_dict['error'] = None
            response_message = query_response_schema.dumps(query_response_dict)
            return func.HttpResponse(response_message,
                                     mimetype='application/json'
                                     )

    logging.info("Searching in done-processing queue")
    messages_done = queue_service.peek_messages(done_queue_name,
                                                num_messages=32
                                                )
    done_schema = query_schema.DoneSchema()
    for m in messages_done:
        decoded_message = done_schema.loads(decode_message(m))
        message_guid = decoded_message['guid']
        message_error = decoded_message['error']
        if message_guid == guid:
            if not message_error:
                query_response_dict['status'] = f'completed'
            else:
                query_response_dict['status'] = f'failed'
            query_response_dict['error'] = message_error
            response_message = query_response_schema.dumps(query_response_dict)
            return func.HttpResponse(response_message,
                                     mimetype='application/json'
                                     )

    error = f'Order {str(guid)} was not found in the queues'
    return func.HttpResponse(error, status_code=400)
