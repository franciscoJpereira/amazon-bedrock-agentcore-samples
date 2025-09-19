import boto3

def get_gatewayID(client: any, gateway_name: str):
    response = client.list_gateways(
        maxResults=10,
    )
    while response:
        for gtw in response.get("items", []):
            if gtw["name"] == gateway_name:
                return gtw["gatewayId"]
        response: dict[str, any] = client.list_gateways(
            maxResults=10,
            nextToken=response["nextToken"]
        )
    raise Exception("User pool not found")



REGION = "eu-central-1"
gateway_client = boto3.client('bedrock-agentcore-control', region_name = REGION)
lambda_client = boto3.client('lambda')
lambda_resp = lambda_client.get_function(FunctionName='gateway_lambda')["Configuration"]

# Replace the AWS Lambda function ARN below
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_resp['FunctionArn'], # Replace this with your AWS Lambda function ARN
            "toolSchema": {
                "inlinePayload": [
                    {
                        "name": "get_order_tool",
                        "description": "tool to get the order",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "orderId": {
                                    "type": "string"
                                }
                            },
                            "required": ["orderId"]
                        }
                    },                    
                    {
                        "name": "update_order_tool",
                        "description": "tool to update the orderId",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "orderId": {
                                    "type": "string"
                                }
                            },
                            "required": ["orderId"]
                        }
                    }
                ]
            }
        }
    }
}
gatewayID = get_gatewayID(gateway_client, "TestGWforLambda")
credential_config = [ 
    {
        "credentialProviderType" : "GATEWAY_IAM_ROLE"
    }
]
targetname='LambdaUsingSDK'
response = gateway_client.create_gateway_target(
    gatewayIdentifier=gatewayID,
    name=targetname,
    description='Lambda Target using SDK',
    targetConfiguration=lambda_target_config,
    credentialProviderConfigurations=credential_config)