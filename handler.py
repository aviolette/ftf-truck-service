import json
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from models import Truck
from src.lambda_utils import (
    created,
    lambda_exception_wrapper,
    no_response,
    not_found,
    ok_json,
    unprocessable,
)

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")

dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)


@lambda_exception_wrapper
def create_truck(event, _context):
    truck = Truck(**json.loads(event["body"]))
    now = datetime.utcnow()
    try:
        ftf_table.put_item(
            Item={
                "PK": f"TRUCK#{truck.id}",
                "SK": f"TRUCK#{truck.id}",
                "type": "TRUCK",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "archived": False,
                "GSI1PK": "TRUCK",
                "GSI1SK": f"ACTIVETRUCK#{truck.id}",
                **truck.dict(),
            },
            TableName=FTF_TABLE,
            ConditionExpression="attribute_not_exists(PK)",
        )
    except Exception as e:
        return unprocessable(str(e))

    return created(truck.dict())


def delete_truck(event, context):
    truck_id = event["pathParameters"]["id"].strip()

    try:
        ftf_table.update_item(
            Key={
                "PK": f"TRUCK#{truck_id}",
                "SK": f"TRUCK#{truck_id}",
            },
            UpdateExpression="SET #archived = :archived, #gsi1sk = :deleted",
            ConditionExpression="attribute_exists(PK)",
            ExpressionAttributeNames={"#archived": "archived", "#gsi1sk": "GSI1SK"},
            ExpressionAttributeValues={
                ":deleted": f"DELETED#{truck_id}",
                ":archived": True,
            },
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return not_found(truck_id)
        raise

    return no_response()


def update_truck(event, _context):
    truck = Truck(**json.loads(event["body"]))
    now = datetime.utcnow()
    try:
        item = ftf_table.update_item(
            Key={
                "PK": f"TRUCK#{truck.id}",
                "SK": f"TRUCK#{truck.id}",
            },
            UpdateExpression="SET name = :name, "
                             "twitter_handle = :twitter_handle, "
                             "url = :url, "
                             "updated_at = :updated",
            ExpressionAttributeValues={
                ":name": truck.name,
                ":twitter_handle": truck.twitter_handle,
                ":url": truck.url,
                ":update_at": now.isoformat(),
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="UPDATED_NEW",
        )

        return ok_json(item.dict())

    except Exception as e:
        return not_found(e)


def get_trucks(_event, _context):
    # TODO: handle pagination
    results = ftf_table.query(
        TableName=FTF_TABLE,
        IndexName="GSI1",
        KeyConditionExpression="#gsi1pk = :type and begins_with(#active, :active)",
        ExpressionAttributeNames={"#gsi1pk": "GSI1PK", "#active": "GSI1SK"},
        ExpressionAttributeValues={":type": "TRUCK", ":active": "ACTIVE"},
    )

    items = [Truck(**item).dict() for item in results.get("Items", [])]

    return ok_json({"data": items})
