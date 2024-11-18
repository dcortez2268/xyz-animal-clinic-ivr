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
tableName = os.environ['PROMPT_TABLE']

# Initialize DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(tableName)

def fetch_prompts(flow, lob=None):
   # query via flow name and optional lob parameter
    try:
        # Query via flow
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('flow').eq(flow)
        )
        items = response.get('Items', [])
        logger.debug(f"Retrieved items: {items}")

        # build returnjson data
        returnJson = {}
        for item in items:
            # Apply additional filtering if flow is 'globalMessages'
            if flow == 'globalMessages' and lob:
                # Skip items that don't match the 'lob' parameter
                if item.get('lob') != lob:
                    continue

            # Extract 'name' and 'english' attributes
            name = item.get('name')
            english = item.get('english')
            if name and english:
                returnJson[name] = english
        
        return returnJson

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e

def lambda_handler(event, context):
    logger.debug(f'event: {event}')
    returnJson = {}

    try:
        # Retrieve the 'flow' and 'lob' parameters
        flow = event['Details']['Parameters']['flow']
        lob = event['Details']['Parameters'].get('lob')
        
        # Fetch prompts from table
        returnJson = fetch_prompts(flow, lob)
        logger.debug(f"Retrieved prompts: {prompts}")
        return returnJson

    except Exception as e:
        logger.error(f"Error in retrieving prompts: {e}")
        raise e
