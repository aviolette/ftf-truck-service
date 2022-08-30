import json
import os
from datetime import datetime

import boto3

from models import Truck
from src.lambda_utils import (
    created,
    lambda_exception_wrapper,
    no_response,
    not_found,
    ok_json,
    unprocessable,
)
from src.trucks import NotFoundException, TruckAlreadyExistsException, TruckService

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")

dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)

truck_service = TruckService(ftf_table)


@lambda_exception_wrapper
def create_truck(event, _context):
    truck = Truck(**json.loads(event["body"]))
    try:
        return created(truck_service.create_truck(truck))
    except TruckAlreadyExistsException as e:
        return unprocessable("Truck already exists")


def delete_truck(event, context):
    truck_id = event["pathParameters"]["id"].strip()
    try:
        truck_service.delete_truck(truck_id)
    except NotFoundException:
        return not_found(f"Truck not found {truck_id}")

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
    return ok_json({"data": truck_service.get_trucks()})
