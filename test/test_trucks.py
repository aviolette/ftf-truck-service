from datetime import datetime

import boto3
import pytest
from moto import mock_dynamodb

from src.models import Truck
from src.trucks import NotFoundException, TruckAlreadyExistsException, TruckService


@pytest.fixture
def truck1():
    return Truck(id="truck1", name="truck1")


@pytest.fixture
def truck2():
    return Truck(id="truck2", name="truck2")


def create_dynamodb():
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table_name = "ftf_engine"
    table = dynamodb.create_table(
        TableName=table_name,
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        KeySchema=[
            {
                "AttributeName": "PK",
                "KeyType": "HASH",
            },
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            }
        ],
    )
    return table


@mock_dynamodb
def test_delete_truck(truck1):
    table = create_dynamodb()
    service = TruckService(table)
    service.create_truck(truck1)

    service.delete_truck(truck1.id)

    item = table.get_item(Key={"PK": "TRUCK#truck1", "SK": "TRUCK#truck1"})
    assert item['Item']['archived']


@mock_dynamodb
def test_delete_truck_not_exists(truck2):
    table = create_dynamodb()
    service = TruckService(table)

    with pytest.raises(NotFoundException):
        service.delete_truck(truck2.id)


@mock_dynamodb
def test_create_truck(truck1):
    table = create_dynamodb()
    service = TruckService(table)

    resp = service.create_truck(truck1)

    assert resp['id'] == truck1.id
    assert resp['name'] == truck1.name


@mock_dynamodb
def test_create_truck_exists(truck1):
    table = create_dynamodb()
    service = TruckService(table)

    service.create_truck(truck1)
    with pytest.raises(TruckAlreadyExistsException):
        service.create_truck(truck1)


@mock_dynamodb
def test_get_trucks_no_data():
    table = create_dynamodb()
    service = TruckService(table)

    items = service.get_trucks()

    assert len(items) == 0


@mock_dynamodb
def test_get_trucks(truck1, truck2):
    table = create_dynamodb()

    now = datetime.utcnow()
    for truck in [truck1, truck2]:
        table.put_item(
            Item={
                "PK": f"TRUCK#{truck.id}",
                "SK": f"TRUCK#{truck.id}",
                "type": "TRUCK",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "archived": False,
                "GSI1PK": "TRUCK",
                "GSI1SK": f"ACTIVETRUCK#{truck.id}",
                "name": truck.name,
            },
            ConditionExpression="attribute_not_exists(PK)",
        )

    service = TruckService(table)

    items = service.get_trucks()

    assert len(items) == 2
    assert items[0]["id"] == "truck1"
    assert items[0]["name"] == "truck1"
    assert items[1]["id"] == "truck2"
    assert items[1]["name"] == "truck2"
