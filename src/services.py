import os

import boto3

from src.locations import AWSLocationService, CacheAndForwardService
from src.vendors import VendorService

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")
dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)

vendor_service = VendorService(ftf_table)
location_service = CacheAndForwardService(
    location_service=AWSLocationService(index_name="FtfEast1", client=boto3.client('location')))
