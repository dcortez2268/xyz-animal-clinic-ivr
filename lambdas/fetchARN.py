import json
import os
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logLevel = os.environ['LOG_LEVEL'].upper()
logger = logging.getLogger()
logger.setLevel(logLevel)

# Initialize the Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name):
    # Retrieve secret
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = response['SecretString']
        return json.loads(secret)
    except ClientError as e:
        logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e

def lambda_handler(event, context):
    logger.debug(f'event: {event}')
    returnJSON = {}

    try:
        # get secret from event
        secret = event['Details']['Parameters']['secret']
        
        # retrieve secret
        secretData = get_secret(secret)
        logger.debug(f"Retrieved secret data: {secretData}")
        returnJSON = secretData
    except Exception as e:
        logger.error(f"Error in retrieving secret: {e}")
        raise e

    return returnJSON
