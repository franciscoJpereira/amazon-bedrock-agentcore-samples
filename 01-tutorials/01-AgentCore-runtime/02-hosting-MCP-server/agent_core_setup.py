from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import time
import os
from utils import get_cognito_data

boto_session = Session()
region = boto_session.region_name
print(f"Using AWS region: {region}")

required_files = ['mcp_server.py', 'requirements.txt']
for file in required_files:
    if not os.path.exists(file):
        raise FileNotFoundError(f"Required file {file} not found")
print("All required files found ✓")

agentcore_runtime = Runtime()
cognito_config = get_cognito_data("MCPServerPool")

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [
            cognito_config['client_id']
        ],
        "discoveryUrl": cognito_config['discovery_url'],
    }
}

print("Configuring AgentCore Runtime...")
response = agentcore_runtime.configure(
    #entrypoint="mcp_server.py",
    auto_create_execution_role=True,
    #auto_create_ecr=True,
    #requirements_file="requirements.txt",
    ecr_repository="715965548279.dkr.ecr.eu-central-1.amazonaws.com/agentcore-athena-test",
    region=region,
    authorizer_configuration=auth_config,
    protocol="MCP",
    agent_name="mcp_server_agentcore"
)
print("Configuration completed ✓")
print("Launching MCP server to AgentCore Runtime...")
print("This may take several minutes...")
launch_result = agentcore_runtime.launch()
print("Launch completed ✓")
print(f"Agent ARN: {launch_result.agent_arn}")
print(f"Agent ID: {launch_result.agent_id}")