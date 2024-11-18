import json
import os
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logLevel = os.environ['LOG_LEVEL'].upper()
logger = logging.getLogger()
logger.setLevel(logLevel)

# Get environment variables
tableName = os.environ['QUEUE_TABLE']

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(tableName)

def get_queue_config(lob, transferFlag='default'):
    try:
        # Query the DynamoDB table using the partition key 'lob'
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('lob').eq(lob)
        )
        
        items = response.get('Items', [])
        logger.debug(f"Retrieved items: {items}")

        # Filter items using a for loop
        for item in items:
            if item.get('transferFlag') == transferFlag:
                # If a match is found, return the queue treatment
                return {
                    "queue": item.get('queue'),
                    "queueTreatment1": item.get('queueTreatment1')
                }

        logger.error(f"No configuration found for lob '{lob}' with transferFlag '{transferFlag}'")
        return {
            "queue": f"{lob}_default"
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e

def lambda_handler(event, context):
    logger.debug(f'event: {event}')
    returnJson = {}

    try:
        # Retrieve the 'lob' and optional 'transferFlag' parameters from the event
        lob = event['Details']['Parameters']['lob']
        transferFlag = event['Details']['Parameters'].get('transferFlag', 'default')
        
        # Get queue configuration
        returnJson = get_queue_config(lob, transferFlag)
        logger.debug(f"Queue configuration result: {returnJson}")
        return returnJson

    except Exception as e:
        logger.error(f"Error in retrieving queue configuration: {e}")
        raise e
