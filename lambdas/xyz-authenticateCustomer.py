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

def authenticate_customer(accountNumber=None, ani=None, ssn=None):
    """
    Query the DynamoDB table using either 'accountNumber' as the primary key
    or 'ani' as the GSI. Validate the 'ssn' attribute if a match is found.
    """
    try:
        # Case 1: Query using accountNumber if it's provided in parameter
        if accountNumber:
            response = table.get_item(Key={'accountNumber': accountNumber})
            item = response.get('Item')
        
        # Case 2: Query using ani (GSI) if accountNumber is not provided
        elif ani:
            response = table.query(
                IndexName='ani-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('ani').eq(ani)
            )
            items = response.get('Items', [])
            item = items[0] if items else None
        
        else:
            logger.error("Either 'accountNumber' or 'ani' must be provided.")
            return {"accountMatches": "0"}

        # If no item is found, return 0 matches
        if not item:
            return {"accountMatches": "0"}

        # Check if the 'ssn' matches
        if item.get('ssn') == ssn:
            return {
                "accountNumber": item.get('accountNumber'),
                "authenticationStatus": "true"
            }
        else:
            return {"accountMatches": "0"}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e

def lambda_handler(event, context):
    logger.debug(f'event: {event}')
    returnJson = {}
    
    try:
        # Retrieve parameters from the event
        accountNumber = event['Details']['Parameters'].get('accountNumber')
        ani = event['Details']['Parameters'].get('ani')
        ssn = event['Details']['Parameters']['ssn']
        
        # Authenticate customer using the available parameters
        returnJson = authenticate_customer(accountNumber=accountNumber, ani=ani, ssn=ssn)
        logger.debug(f"Authentication data: {returnJson}")
        return returnJson

    except Exception as e:
        logger.error(f"Error in customer authentication: {e}")
        raise e
