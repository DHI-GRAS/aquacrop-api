import logging
import os
import base64
import uuid
import json

from marshmallow.exceptions import ValidationError
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

from . import submit_schema


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
    table_service = TableService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )

    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Post"
    }

    schema = submit_schema.SubmitMessageSchema()
    try:
        job_dict = schema.loads(req.get_body())
    except ValidationError:
        error = f'Failed to validate the submit message'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )

    table_name = os.getenv('AZURE_TABLE_NAME')
    table_service.create_table(table_name)
    guid = uuid.uuid4()
    try:
        job_dict = schema.dump(job_dict)
    except ValidationError:
        error = f'Failed to submit job'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )
    entity = Entity()
    entity.PartitionKey = 'await'
    entity.RowKey = str(guid)
    entity.Error = ""
    entity.area_name = job_dict['area_name']
    entity.crop = job_dict['crop']
    entity.planting_date = job_dict['planting_date']
    entity.irrigated = job_dict['irrigated']
    entity.fraction = job_dict['fraction']
    entity.geometry = json.dumps(job_dict['geometry'])
    try:
        table_service.insert_entity(table_name, entity)
    except TypeError:
        error = f'Failed to insert to table'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )

    response_dict = {}
    response_dict['guid'] = guid
    schema = submit_schema.SubmitResponseSchema()
    response_message = schema.dumps(response_dict)
    return func.HttpResponse(response_message,
                             headers=headers_dict,
                             mimetype='application/json'
                             )
