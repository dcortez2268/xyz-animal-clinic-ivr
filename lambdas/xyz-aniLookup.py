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
tableName = os.environ['CUSTOMER_TABLE']

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(tableName)

def lookup_by_ani(ani):
    # implement GSI query
    try:
        response = table.query(
            IndexName='ani-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('ani').eq(ani)
        )
        
        items = response.get('Items', [])
        logger.debug(f"Retrieved items: {items}")

        # If items are found, return accountNumber and count of matches
        if items:
            accountNumber = items[0].get('accountNumber')
            return {
                "accountNumber": accountNumber,
                "accountMatches": len(items)
            }
        else:
            return {"accountMatches": 0}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"accountMatches": 0}

def lambda_handler(event, context):
    logger.debug(f'event: {event}')
    returnJson = {}
    
    try:
        ani = event['Details']['Parameters']['ani']
        
        # query via 'ani'
        returnJson = lookup_by_ani(ani)
        logger.debug(f" result: {returnJson}")
        return returnJson

    except Exception as e:
        logger.error(f"Error in ANI lookup: {e}")
        return {"accountMatches": 0}
