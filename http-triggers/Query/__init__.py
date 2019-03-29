import os
import logging
import binascii
import base64
import uuid

from azure.cosmosdb.table.tableservice import TableService
from azure.storage import CloudStorageAccount
from azure.common import AzureMissingResourceHttpError
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

    table_name = os.getenv('AZURE_TABLE_NAME')
    table_service = TableService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT'),
        account_key=os.getenv('AZURE_STORAGE_ACCESS_KEY')
    )

    headers_dict = {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "Get"
    }
    guid = req.params.get('guid')
    if not guid:
        error = f'Check Url paramaters. No guid variable was found'
        return func.HttpResponse(error,
                                 headers=headers_dict,
                                 status_code=400
                                 )
    logging.info("Creating Dicts")
    query_response_dict = {}
    query_response_schema = query_schema.QueryResponseSchema()
    retrieved_entity = None
    logging.info("Searching in await-processing queue")
    try:
        retrieved_entity = table_service.get_entity(table_name, 'await', str(guid))
    except AzureMissingResourceHttpError:
        pass

    if retrieved_entity:
        message_error = retrieved_entity.Error or None
        query_response_dict['status'] = f'await'
        query_response_dict['error'] = message_error
        response_message = query_response_schema.dumps(query_response_dict)
        return func.HttpResponse(response_message,
                                 headers=headers_dict,
                                 mimetype='application/json'
                                 )

    logging.info("Searching in processing queue")
    try:
        retrieved_entity = table_service.get_entity(table_name, 'processing', str(guid))
    except AzureMissingResourceHttpError:
        pass

    if retrieved_entity:
        message_error = retrieved_entity.Error or None
        query_response_dict['status'] = f'processing'
        query_response_dict['error'] = message_error
        response_message = query_response_schema.dumps(query_response_dict)
        return func.HttpResponse(response_message,
                                 headers=headers_dict,
                                 mimetype='application/json'
                                 )

    logging.info("Searching in done-processing table")
    try:
        retrieved_entity = table_service.get_entity(table_name, 'done', str(guid))
    except AzureMissingResourceHttpError:
        pass

    if retrieved_entity:
        message_error = retrieved_entity.Error or None
        if not message_error:
            query_response_dict['status'] = f'completed'
        else:
            query_response_dict['status'] = f'failed'
        query_response_dict['error'] = message_error
        response_message = query_response_schema.dumps(query_response_dict)
        return func.HttpResponse(response_message,
                                 headers=headers_dict,
                                 mimetype='application/json'
                                 )

    error = f'Order {str(guid)} was not found'
    return func.HttpResponse(error,
                             headers=headers_dict,
                             status_code=400)
