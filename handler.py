import json
import os
from datetime import datetime

import boto3

from lambda_utils import created, lambda_exception_wrapper, ok_json, unprocessable
from models import Truck

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")

dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)


@lambda_exception_wrapper
def create_truck(event, _context):
    truck = Truck(**json.loads(event['body']))
    now = datetime.utcnow()
    try:
        ftf_table.put_item(
            Item={
                "PK": f"TRUCK#{truck.id}",
                "SK": f"TRUCK#{truck.id}",
                "type": "TRUCK",
                "created_at": now.isoformat(),
                "GSI1PK": "TRUCK",
                "GSI1SK": f"ACTIVETRUCK#{truck.id}",
                "twitter_handle": truck.twitter_handle,
                "url": truck.url,
                "archived": False,
                "name": truck.name
            },
            TableName=FTF_TABLE,
            ConditionExpression="attribute_not_exists(PK)",
        )
    except Exception as e:
        return unprocessable(str(e))

    return created(truck.dict())


def get_trucks(_event, _context):
    results = ftf_table.query(
        TableName=FTF_TABLE,
        IndexName="GSI1",
        KeyConditionExpression="#gsi1pk = :type and begins_with(#active, :active)",
        ExpressionAttributeNames={"#gsi1pk": "GSI1PK", "#active": "GSI1SK"},
        ExpressionAttributeValues={
            ":type": "TRUCK",
            ":active": "ACTIVE"
        },
    )

    items = [Truck(**item).dict() for item in results.get("Items", [])]

    return ok_json({"data": items})
