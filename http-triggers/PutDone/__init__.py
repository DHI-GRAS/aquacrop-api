import os
import logging
import base64

from marshmallow.exceptions import ValidationError
import azure.functions as func

from azure.common import AzureMissingResourceHttpError
from azure.cosmosdb.table.tableservice import TableService
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

    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Post"
    }
    schema = put_schema.DoneSchema()
    try:
        done_dict = schema.loads(req.get_body())
    except ValidationError:
        error = f'Failed to validate the done message'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )

    table_name = os.getenv('AZURE_TABLE_NAME')
    table_service = TableService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )
    try:
        entity = table_service.get_entity(table_name, 'processing', done_dict['guid'])
    except AzureMissingResourceHttpError:
        error = f'Failed to put done message'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )
    if not done_dict['error']:
        entity.Error = ""
    else:
        entity.Error = done_dict['error']
    table_service.delete_entity(table_name, entity.PartitionKey, entity.RowKey)
    entity.PartitionKey = 'done'
    table_service.insert_entity(table_name, entity)

    return func.HttpResponse('Message was successfully inserted into Done queue',
                             headers=headers_dict
                             )
