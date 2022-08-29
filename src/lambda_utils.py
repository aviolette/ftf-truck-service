import json

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.parser import (
    ValidationError,
)


class UnprocessableException(Exception):
    pass


@lambda_handler_decorator
def lambda_exception_wrapper(handler, event, context):
    try:
        response = handler(event, context)
    except UnprocessableException as e:
        return unprocessable(str(e))
    except ValidationError as e:
        return unprocessable(str(e.raw_errors[0].exc))
    return response


def redirect(url: str) -> dict:
    return {
        "statusCode": 302,
        "headers": {"Location": url},
    }


def created(body: dict):
    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def no_response():
    return {"statusCode": 204}


def not_found(message):
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }


def unprocessable(message):
    return {
        "statusCode": 422,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }


def ok_json(body: dict):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def query_param(event, name, default=None):
    return event.get("queryStringParameters", {}).get(name, default)


def email_from_event(event):
    return _lambda_auth(event)["email"]


def access_token_from_event(event):
    return _lambda_auth(event)["token"]


def _lambda_auth(event):
    return event["requestContext"]["authorizer"]["lambda"]
