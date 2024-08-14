# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from datetime import datetime

import boto3

from schema.uni_prop_prod_shared_local_sandesh.contractstatuschanged import (
AWSEvent, ContractStatusChanged, Marshaller)

# from schema.uni_prop_prod_shared_local_sandesh.contractstatuschanged.marshaller import Marshaller
# from schema.uni_prop_prod_shared_local_sandesh.contractstatuschanged.AWSEvent import AWSEvent
# from schema.uni_prop_prod_shared_local_sandesh.contractstatuschanged.ContractStatusChanged import ContractStatusChanged


# Initialise Environment variables
if (SERVICE_NAMESPACE := os.environ.get("SERVICE_NAMESPACE")) is None:
    raise InternalServerError("SERVICE_NAMESPACE environment variable is undefined")
if (CONTRACT_STATUS_TABLE := os.environ.get("CONTRACT_STATUS_TABLE")) is None:
    raise InternalServerError("CONTRACT_STATUS_TABLE environment variable is undefined")


# Initialise boto3 clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(CONTRACT_STATUS_TABLE)  # type: ignore

# Get current date
now = datetime.now()
current_date = now.strftime("%d/%m/%Y %H:%M:%S")


def lambda_handler(event, context):
    """Event handler for ContractStatusChangedEvent

    Parameters
    ----------
    event: dict, required
        Event Bridge Events Format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
        The same input event file
    """
    #Deserialize event into strongly typed object
    awsEvent:AWSEvent = Marshaller.unmarshall(event, AWSEvent)
    detail:ContractStatusChanged = awsEvent.detail
    save_contract_status(detail)

    save_contract_status(detail)

    # return OK, async function
    return {
        "statusCode": 200,
    }


def save_contract_status(contract_status_changed_event):
    """Saves contract status in contract status table

    Args:
        contract_status_changed_event (dict):
            Contract_status_changed_event

    Returns:
        dict: _description_
    """
    print("Saving contract status to contract status table. %s", contract_status_changed_event.contract_id)

    return table.update_item(
                    Key={
                        'property_id': contract_status_changed_event.property_id
                    },
                    UpdateExpression="set contract_status=:t, contract_last_modified_on=:m, contract_id=:c",
                    ExpressionAttributeValues={
                        ':c': contract_status_changed_event.contract_id,
                        ':t': contract_status_changed_event.contract_status,
                        ':m': contract_status_changed_event.contract_last_modified_on
                    }
            )
