import os
import logging
import base64
import binascii
import json

from marshmallow.exceptions import ValidationError
from azure.storage import CloudStorageAccount
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

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
    table_service = TableService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )

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
    table_name = os.getenv('AZURE_TABLE_NAME')
    entity = None
    entities = table_service.query_entities(table_name, filter="PartitionKey eq 'await'")
    for entity in entities:
        break
    if not entity:
        return func.HttpResponse(f'No job found',
                                 headers=headers_dict,
                                 status_code=400
                                 )
    message = {}
    message['crop'] = entity.crop
    message['geometry'] = json.loads(entity.geometry)
    message['irrigated'] = entity.irrigated
    message['guid'] = entity.RowKey
    message['area_name'] = entity.area_name
    message['planting_date'] = entity.planting_date
    message['fraction'] = entity.fraction

    table_service.delete_entity(table_name, entity.PartitionKey, entity.RowKey)
    entity.PartitionKey = 'processing'

    table_service.insert_entity(table_name, entity)

    return func.HttpResponse(json.dumps(message),
                             headers=headers_dict,
                             mimetype='application/json'
                             )
