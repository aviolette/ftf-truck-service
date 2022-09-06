import os

import boto3

from src.vendors import VendorService

FTF_TABLE = os.environ.get("FTF_TABLE", "ftf_engine")
dynamodb = boto3.resource("dynamodb")
ftf_table = dynamodb.Table(FTF_TABLE)

vendor_service = VendorService(ftf_table)
