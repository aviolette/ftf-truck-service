from datetime import datetime

from botocore.exceptions import ClientError

from src.models import Vendor


class VendorAlreadyExistsException(Exception):
    pass


class NotFoundException(Exception):
    pass


class VendorService:
    def __init__(self, ftf_table):
        self.ftf_table = ftf_table

    def get_vendors(self):
        # TODO: handle pagination
        results = self.ftf_table.query(
            IndexName="GSI1",
            KeyConditionExpression="#gsi1pk = :type and begins_with(#active, :active)",
            ExpressionAttributeNames={"#gsi1pk": "GSI1PK", "#active": "GSI1SK"},
            ExpressionAttributeValues={":type": "VENDOR", ":active": "ACTIVE"},
        )
        return [Vendor(**item).dict() for item in results.get("Items", [])]

    def create_vendor(self, vendor) -> dict:
        now = datetime.utcnow()
        try:
            self.ftf_table.put_item(
                Item={
                    "PK": f"VENDOR#{vendor.id}",
                    "SK": f"VENDOR#{vendor.id}",
                    "type": "VENDOR",
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                    "archived": False,
                    "GSI1PK": "VENDOR",
                    "GSI1SK": f"ACTIVEVENDOR#{vendor.id}",
                    **vendor.dict(),
                },
                ConditionExpression="attribute_not_exists(PK)",
            )

            response = self.ftf_table.get_item(
                Key={"PK": f"VENDOR#{vendor.id}", "SK": f"VENDOR#{vendor.id}"}
            )

            return Vendor(**response.get("Item")).dict()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise VendorAlreadyExistsException()
            raise

    def delete_vendor(self, vendor_id: str):
        try:
            self.ftf_table.update_item(
                Key={
                    "PK": f"VENDOR#{vendor_id}",
                    "SK": f"VENDOR#{vendor_id}",
                },
                UpdateExpression="SET #archived = :archived, #gsi1sk = :deleted",
                ConditionExpression="attribute_exists(PK)",
                ExpressionAttributeNames={"#archived": "archived", "#gsi1sk": "GSI1SK"},
                ExpressionAttributeValues={
                    ":deleted": f"DELETED#{vendor_id}",
                    ":archived": True,
                },
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise NotFoundException(vendor_id)
            raise

    def update_vendor(self, vendor):
        now = datetime.utcnow()
        try:
            item = self.ftf_table.update_item(
                Key={
                    "PK": f"VENDOR#{truck.id}",
                    "SK": f"VENDOR#{truck.id}",
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

            return item.dict()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise NotFoundException(truck.id)
            raise
