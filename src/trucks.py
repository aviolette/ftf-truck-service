from datetime import datetime

from botocore.exceptions import ClientError

from models import Truck


class TruckAlreadyExistsException(Exception):
    pass


class NotFoundException(Exception):
    pass


class TruckService:
    def __init__(self, ftf_table):
        self.ftf_table = ftf_table

    def get_trucks(self):
        # TODO: handle pagination
        results = self.ftf_table.query(
            IndexName="GSI1",
            KeyConditionExpression="#gsi1pk = :type and begins_with(#active, :active)",
            ExpressionAttributeNames={"#gsi1pk": "GSI1PK", "#active": "GSI1SK"},
            ExpressionAttributeValues={":type": "TRUCK", ":active": "ACTIVE"},
        )
        return [Truck(**item).dict() for item in results.get("Items", [])]

    def create_truck(self, truck) -> dict:
        now = datetime.utcnow()
        try:
            self.ftf_table.put_item(
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
                ConditionExpression="attribute_not_exists(PK)",
            )

            response = self.ftf_table.get_item(
                Key={"PK": f"TRUCK#{truck.id}", "SK": f"TRUCK#{truck.id}"}
            )

            return Truck(**response.get("Item")).dict()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise TruckAlreadyExistsException()
            raise

    def delete_truck(self, truck_id):
        try:
            self.ftf_table.update_item(
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
                raise NotFoundException(truck_id)
            raise
