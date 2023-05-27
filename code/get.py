import os
import boto3
import datetime

DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')

session = boto3.Session()
dynamodb = session.resource('dynamodb', region_name='eu-west-1')

def get_current_pull_requests() -> dict:
    table = dynamodb.Table(DYNAMO_TABLE)
    response = table.get_item(
        Key={
            'timestamp': str(datetime.datetime.now().strftime("%Y-%m-%d-%H")),
        }
    )
    return response['Item']['pull_requests']


def lambda_handler(event, context):
    recent_pull_requests = get_current_pull_requests()
    return {
        'statusCode': 200,
        'body': recent_pull_requests
    }


if __name__ == '__main__':
    print(lambda_handler(None, None))
