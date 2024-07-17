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


def create_contract(event: dict) -> None:
    """Create contract inside DynamoDB table

    Execution logic:
        if contract does not exist
        or contract status is either of [ CANCELLED | CLOSED | EXPIRED]
        then
            create or replace contract with status = DRAFT
            log response
            log trace info
            return
        else
            log exception message

    Parameters
    ----------
        contract (dict): _description_

    Returns
    -------
    dict
        DynamoDB put Item response
    """

    # TODO: create entry in DDB for new contract
    raise NotImplementedError


def update_contract(contract: dict) -> None:
    """Update an existing contract inside DynamoDB table

    Execution logic:

        if  contract exists exist
        and contract status is either of [ DRAFT ]
        then
            update contract status to APPROVED
            log response
            log trace info
            return
        else
            log exception message

    Parameters
    ----------
        contract (dict): _description_

    Returns
    -------
    dict
        DynamoDB put Item response
    """

    # TODO: add code to update the contract in DynamoDB table
    raise NotImplementedError
