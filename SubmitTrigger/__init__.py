import logging

import azure.functions as func
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_body()
        data = json.loads(req_body)
        name = data['name']
    except ValueError:
        logging.info("ValueError")
        pass

    return func.HttpResponse(f"Hello {name}!")
