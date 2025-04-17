import boto3
import json
import os
import datetime

{% if copier__dynamo_db %}
def get_dynamodb_client():
    """Get a DynamoDB client, either for local or AWS"""
    dynamodb_endpoint = os.environ.get("DYNAMODB_ENDPOINT")

    if dynamodb_endpoint:
        # For local development
        return boto3.client("dynamodb", endpoint_url=dynamodb_endpoint)
    else:
        # For AWS deployment
        return boto3.client("dynamodb")
{%- endif %}

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    {% if copier__dynamo_db %}
    dynamodb = get_dynamodb_client()
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")

    # Example DynamoDB operation
    source_ip = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown")
    timestamp = datetime.datetime.now().isoformat()
    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                'ip_address': {'S': source_ip},
                'timestamp': {'S': timestamp},
            }
        )
    except Exception as e:
        return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    {%- endif %}
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
