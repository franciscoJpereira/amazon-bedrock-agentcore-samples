import utils
import boto3

from strands import Agent
import logging
from strands.models import BedrockModel
from mcp.client.streamable_http import streamablehttp_client 
from strands.tools.mcp.mcp_client import MCPClient
from strands import Agent

# Configure the root strands logger. Change it to DEBUG if you are debugging the issue.
logging.getLogger("strands").setLevel(logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

REGION = "eu-central-1"
CLIENT_NAME = "sample-agentcore-gateway-client"
RESOURCE_SERVER_ID = "sample-agentcore-gateway-id"
#data = utils.get_cognito_data("sample-agentcore-gateway-pool")
user_pool_id = "eu-central-1_gDl408iC2"
client_id = "66983tat2j73j86spqarjidc4a"
cognito = boto3.client("cognito-idp", region_name=REGION)
scopeString = f"{RESOURCE_SERVER_ID}/gateway:read {RESOURCE_SERVER_ID}/gateway:write"
client_id, client_secret  = utils.get_or_create_m2m_client(cognito, user_pool_id, CLIENT_NAME, RESOURCE_SERVER_ID)


print("Requesting the access token from Amazon Cognito authorizer...May fail for some time till the domain name propogation completes")
token_response = utils.get_token(user_pool_id, client_id, client_secret,scopeString,REGION)
token = token_response["access_token"]
print("Token response:", token)

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

agcore_c = boto3.client("bedrock-agentcore-control")
gtw_id = get_gatewayID(agcore_c, "TestGWforLambda")
gatewayURL = agcore_c.get_gateway(gatewayIdentifier=gtw_id)["gatewayUrl"]

def create_streamable_http_transport():
    return streamablehttp_client(gatewayURL,headers={"Authorization": f"Bearer {token}"})

client = MCPClient(create_streamable_http_transport)

## The IAM credentials configured in ~/.aws/credentials should have access to Bedrock model
yourmodel = BedrockModel(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    temperature=0.7,
)
targetname='LambdaUsingSDK'
with client:
    # Call the listTools 
    tools = client.list_tools_sync()
    # Create an Agent with the model and tools
    agent = Agent(model=yourmodel,tools=tools) ## you can replace with any model you like
    print(f"Tools loaded in the agent are {agent.tool_names}")
    # print(f"Tools configuration in the agent are {agent.tool_config}")
    # Invoke the agent with the sample prompt. This will only invoke  MCP listTools and retrieve the list of tools the LLM has access to. The below does not actually call any tool.
    agent("Hi , can you list all tools available to you")
    # Invoke the agent with sample prompt, invoke the tool and display the response
    agent("Check the order status for order id 123 and show me the exact response from the tool")
    # Call the MCP tool explicitly. The MCP Tool name and arguments must match with your AWS Lambda function or the OpenAPI/Smithy API
    result = client.call_tool_sync(
    tool_use_id="get-order-id-123-call-1", # You can replace this with unique identifier. 
    name=targetname+"___get_order_tool", # This is the tool name based on AWS Lambda target types. This will change based on the target name
    arguments={"orderId": "123"}
    )
    # Print the MCP Tool response
    print(f"Tool Call result: {result['content'][0]['text']}")