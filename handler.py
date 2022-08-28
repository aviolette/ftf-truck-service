import os

import boto3

from lambda_utils import ok_json
from models import Truck

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")

dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)


def create_trucks(event, _context):
    return {"statusCode": 201}


def get_trucks(_event, _context):
    results = ftf_table.query(
        TableName=FTF_TABLE,
        IndexName="GSI1",
        KeyConditionExpression="#gsi1pk = :type",
        ExpressionAttributeNames={"#gsi1pk": "GSI1PK"},
        ExpressionAttributeValues={
            ":type": "TRUCK",
        },
    )

    items = results.get("Items", [])

    items = [Truck(**item).dict() for item in items]

    return ok_json({"data": items})
