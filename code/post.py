import os
import json
import requests
import datetime

import boto3

DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')


session = boto3.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')


def get_current_pull_requests() -> dict:
    response = requests.get('https://api.github.com/repos/octocat/Hello-World/pulls')
    table = dynamodb.Table(DYNAMO_TABLE)
    table.put_item(
        Item={
            'timestamp': str(datetime.datetime.now().strftime("%Y-%m-%d-%H")),
            'pull_requests': response.json(),
        }
    )
    return response.json()


def lambda_handler(event, context):
    recent_pull_requests = get_current_pull_requests()
    return {
        'statusCode': 200,
        'body': json.dumps(recent_pull_requests)
    }


if __name__ == '__main__':
    print(lambda_handler(None, None))
