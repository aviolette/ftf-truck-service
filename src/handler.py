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
from src.models import Vendor
from src.vendors import NotFoundException, VendorAlreadyExistsException, VendorService

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")
dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)
vendor_service = VendorService(ftf_table)


@lambda_exception_wrapper
def create_vendor(event, _context):
    vendor = Vendor(**json.loads(event["body"]))
    try:
        return created(vendor_service.create_vendor(vendor))
    except VendorAlreadyExistsException as e:
        return unprocessable("Truck already exists")


@lambda_exception_wrapper
def delete_vendor(event, context):
    truck_id = event["pathParameters"]["id"].strip()
    try:
        vendor_service.delete_vendor(truck_id)
    except NotFoundException:
        return not_found(f"Truck not found {truck_id}")

    return no_response()


@lambda_exception_wrapper
def update_vendor(event, _context):
    truck = Vendor(**json.loads(event["body"]))
    try:
        updated = vendor_service.update_vendor(truck)
        return ok_json(updated)
    except NotFoundException:
        return not_found(f"Truck not found {truck.id}")


def get_vendors(_event, _context):
    return ok_json({"data": vendor_service.get_vendors()})
