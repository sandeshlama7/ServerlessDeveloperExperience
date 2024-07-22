# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import json
import uuid
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from contracts_service.enums import ContractStatus

# Initialise Environment variables
if (SERVICE_NAMESPACE := os.environ.get("SERVICE_NAMESPACE")) is None:
    raise EnvironmentError("SERVICE_NAMESPACE environment variable is undefined")
if (DYNAMODB_TABLE := os.environ.get("DYNAMODB_TABLE")) is None:
    raise EnvironmentError("DYNAMODB_TABLE environment variable is undefined")

# Initialise boto3 clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)  # type: ignore


def lambda_handler(event: dict, context: dict):
    # Multiple records can be delivered in a single event
    for record in event['Records']:
        http_method = record['messageAttributes'].get('HttpMethod', {}).get('stringValue')
        body = json.loads(record['body'])

        if http_method == 'POST':
            create_contract(body)
        elif http_method == 'PUT':
            update_contract(body)
        else:
            raise Exception(f'Unable to handle HttpMethod {http_method}')


def update_contract(contract: dict) -> None:

    print(f"Updating contract: {contract}")

    try:
        contract["contract_status"] = ContractStatus.APPROVED.name
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        response = table.update_item(
            Key={
                'property_id': contract['property_id'],
            },
            UpdateExpression="set contract_status=:t, modified_date=:m",
            ConditionExpression=
                Attr('property_id').exists()
              & Attr('contract_status').is_in([
                  ContractStatus.DRAFT.name
                ]),
            ExpressionAttributeValues={
                ':t': contract['contract_status'],
                ':m': current_date,
            },
            ReturnValues="UPDATED_NEW")
        print(f'var:response - "{response}"')

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == 'ConditionalCheckFailedException':
            print(f"Unable to update contract Id {contract['property_id']}. Status is not in status DRAFT")
        elif code == 'ResourceNotFoundException':
            print(f"Unable to update contract Id {contract['property_id']}. Not Found")
        else:
            raise e


def create_contract(event: dict) -> None:

    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    contract = {
        "property_id":                  event["property_id"],  # PK
        "address":                      event["address"],
        "seller_name":                  event["seller_name"],
        "contract_created":             current_date,
        "contract_last_modified_on":    current_date,
        "contract_id":                  str(uuid.uuid4()),
        "contract_status":              ContractStatus.DRAFT.name,
    }

    print(f"Creating contract: {contract} From event: {event}")

    try:
        response = table.put_item(
            Item=contract,
            ConditionExpression=
                Attr('property_id').not_exists()
              | Attr('contract_status').is_in([
                  ContractStatus.CANCELLED.name,
                  ContractStatus.CLOSED.name,
                  ContractStatus.EXPIRED.name,
                ]))
        print(f'var:response - "{response}"')

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == 'ConditionalCheckFailedException':
            print(f"""
                    Unable to create contract for Property {contract['property_id']}.
                    There already is a contract for this property in status {ContractStatus.DRAFT.name} or {ContractStatus.APPROVED.name}
                    """)
        else:
            raise e
