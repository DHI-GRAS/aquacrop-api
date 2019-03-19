import os
import logging
import binascii
import base64
import uuid
import random

import azure.functions as func
from azure.storage import CloudStorageAccount

from . import move_schema


def encode_message(msg):
    try:
        # ensure bytes
        msg = msg.encode('utf-8')
    except AttributeError:
        pass
    return base64.b64encode(msg).decode('utf-8')


def decode_message(queue_message):
    try:
        msg = base64.b64decode(queue_message.content).decode('utf-8')
    except binascii.Error:
        msg = queue_message.content
    return msg


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP Move trigger received a request')

    logging.debug('Creating queue service')
    account = CloudStorageAccount(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )
    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Get"
    }
    queue_service = account.create_queue_service()

    guid = req.params.get('guid')
    if not guid:
        error = f'Check Url paramaters. No guid variable was found'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )
    guid = uuid.UUID(guid)
    logging.info("Creating Dicts")
    await_queue_name = os.getenv('AZURE_AWAIT_QUEUE_NAME')
    done_queue_name = os.getenv('AZURE_DONE_QUEUE_NAME')

    logging.info("Searching in await-processing queue")
    messages_awaiting = queue_service.get_messages(
        await_queue_name,
        num_messages=32
    )
    messages_info_by_guid = {}
    await_schema = move_schema.AwaitSchema()
    found = False
    for m in messages_awaiting:
        message_guid = await_schema.loads(decode_message(m))['guid']
        messages_info_by_guid[message_guid] = (m.id, m.pop_receipt)
        if message_guid == guid:
            found = True
            break
    if found:
        [m_id, m_pop_receipt] = messages_info_by_guid[guid]
        queue_service.delete_message(await_queue_name, m_id, m_pop_receipt)
        done_schema = move_schema.DoneSchema()
        done_dict = {}
        done_dict['guid'] = guid
        done_dict['error'] = random.sample([None, "random error"], 1)[0]
        message = done_schema.dumps(done_dict)
        queue_service.put_message(
            queue_name=done_queue_name,
            content=encode_message(message),
            time_to_live=604800
        )
        return func.HttpResponse(f'Ok',
                                 headers=headers_dict,
                                 status_code=400
                                 )
    else:
        return func.HttpResponse(f'Not found',
                                 headers=headers_dict,
                                 status_code=400
                                 )
