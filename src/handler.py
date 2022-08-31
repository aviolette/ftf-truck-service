import json
import os

import boto3

from src.lambda_utils import (
    created,
    lambda_exception_wrapper,
    no_response,
    not_found,
    ok_json,
    unprocessable,
)
from src.models import Truck
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


@lambda_exception_wrapper
def delete_truck(event, context):
    truck_id = event["pathParameters"]["id"].strip()
    try:
        truck_service.delete_truck(truck_id)
    except NotFoundException:
        return not_found(f"Truck not found {truck_id}")

    return no_response()


@lambda_exception_wrapper
def update_truck(event, _context):
    truck = Truck(**json.loads(event["body"]))
    try:
        updated = truck_service.update_truck(truck)
        return ok_json(updated)
    except NotFoundException:
        return not_found(f"Truck not found {truck.id}")


def get_trucks(_event, _context):
    return ok_json({"data": truck_service.get_trucks()})
