import logging
import os
import azure.functions as func
import base64
import uuid
from . import submit_schema

from marshmallow.exceptions import ValidationError
from azure.storage import CloudStorageAccount


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
    queue_service = account.create_queue_service()
    schema = submit_schema.SubmitMessageSchema()
    try:
        job_dict = schema.loads(req.get_body())
    except ValidationError:
        error = f'Failed to validate the submit message'
        return func.HttpResponse(error, status_code=400)

    await_queue_name = os.getenv('AZURE_AWAIT_QUEUE_NAME')
    guid = uuid.uuid4()
    job_dict['guid'] = guid
    schema = submit_schema.SubmitJobSchema()
    try:
        message = schema.dumps(job_dict)
    except ValidationError:
        error = f'Failed to submit job'
        return func.HttpResponse(error, status_code=400)

    queue_service.put_message(
        queue_name=await_queue_name,
        content=encode_message(message),
        time_to_live=604800
    )
    response_dict = {}
    response_dict['guid'] = guid
    schema = submit_schema.SubmitResponseSchema()
    response_message = schema.dumps(response_dict)
    return func.HttpResponse(response_message, mimetype='application/json')
