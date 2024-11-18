import json
import os
import boto3
import logging

# Set up logging
logLevel = os.environ['LOG_LEVEL'].upper()
logger = logging.getLogger()
logger.setLevel(logLevel)

# Get environment variables
tableName = os.environ['DNIS_TABLE'] 

# Initialize DynamoDB resource and table 
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(tableName)

def lambda_handler(event, context):
    logger.debug(event)
    returnJSON = {}
   
    try:
        dnis = event['Details']['Parameters']['dnis']
    except Exception:
        logger.error("No 'dnis' parameter provided in the event.")
        raise Exception('Missing DNIS parameter.')

    try:
        # Query the DynamoDB table using the partition key 'dnis'
        response = table.get_item(Key={'dnis': dnis})
        item = response.get('Item')
        if not item:
            # no item found
            logger.error(f"No configuration found for DNIS {dnis}.")
            raise Exception(f"No configuration found for DNIS {dnis}.")
        else:
            returnJSON = item
            logger.debug(f"Retrieved item: {returnJSON}")
    except Exception as e:
        # Log and re-raise exceptions
        logger.error(f"Exception occurred while retrieving DNIS configuration: {e} ")
        raise e

    return returnJSON
