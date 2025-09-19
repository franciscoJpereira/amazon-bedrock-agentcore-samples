import yaml
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import argparse
import time
from IPython.display import Markdown, display

boto_session = Session()
region = boto_session.region_name

def setup_runtime() -> Runtime:
    agentcore_runtime = Runtime()
    agent_name = "strands_claude_getting_started"
    response = agentcore_runtime.configure(
        entrypoint="agent.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name
    )

    print(response)
    return agentcore_runtime



def launch():
    runtime = setup_runtime()
    result = runtime.launch()
    print(result)

def check_status():
    runtime = setup_runtime()
    status_response = runtime.status()
    status = status_response.endpoint["status"]
    end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']
    while status not in end_status:
        time.sleep(10)
        status_response = runtime.status()
        status = status_response.endpoint['status']
        print(status)
    print(status)

def call_runtime(prompt: str):
    runtime = setup_runtime()
    _ = runtime.invoke(
        {
            "prompt": prompt
        }
    )

def clean_bucket(bucket: str):
    print(bucket)
    if not bucket:
        return
    client = boto_session.client("s3")
    objects: list[dict] = client.list_objects(
        Bucket=bucket,
    ).get("contents", None)
    while objects:
        client.delete_objects(
            Bucket=bucket,
            Delete=objects
        )
        objects: list[dict] = client.list_objects(
            Bucket=bucket,
        ).get("contents", None)
    
    result = client.delete_bucket(
        Bucket=bucket,
    )
    print(result)

def codebuild_cleanup(
    project: str,
):
    print(project)
    if not project:
        return
    cb = boto_session.client("codebuild")
    result = cb.delete_project(
        name=project
    )
    print(result)

def clean_roles(
        agent_role: str,
        codebuild_role: str,
):
    print(agent_role, codebuild_role)
    iam = boto_session.client("iam")
    if agent_role:
        result = iam.delete_role(
            RoleName=agent_role
        )
        print(result)
    if codebuild_role:
        result = iam.delete_role(
            RoleName=codebuild_role
        )
        print(result)

def clean_agent(
        agent_id: str
):
    print(agent_id)
    if not agent_id:
        return
    ac = boto_session.client("bedrock-agentcore-control")
    result = ac.delete_agent_runtime(
        agentRuntimeId=agent_id
    )
    print(result)

def clean_ecr(
        ecr_repository: str
):
    print(ecr_repository)
    if not ecr_repository:
        return
    ecr = boto_session.client("ecr")
    result = ecr.delete_repository(
        repositoryName=ecr_repository,
        force=True
    )
    print(result)

def cleanup():
    data: dict = {}
    with open(".bedrock_agentcore.yaml") as f:
        data = yaml.safe_load(f)
    agents: dict = data.get("agents", {})
    for agent_k in agents:
        agent: dict = agents.get(agent_k)
        bucket = agent.get("codebuild", {}).get("source_bucket", "")
        ecr_repository = agent.get("aws", {}).get("ecr_repository", "")
        agent_role = agent.get("aws", {}).get("execution_role", "")
        agent_arn = agent.get("bedrock_agentcore", {}).get("agent_id", "")
        codebuild_role = agent.get("codebuild", {}).get("execution_role", "")
        codebuild_project = agent.get("codebuild", {}).get("project_name", "")

        clean_bucket(bucket)
        codebuild_cleanup(codebuild_project)
        clean_agent(agent_arn)
        clean_ecr(ecr_repository)
        clean_roles(agent_role, codebuild_role)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("op")
    parser.add_argument(
        "--prompt",
        default="Tell a joke."
    )
    args = parser.parse_args()
    match args.op:
        case "setup":
            setup_runtime()
        case "launch":
            launch()
        case "status":
            check_status()
        case "call":
            prompt = args.prompt
            call_runtime(prompt)
        case "clean":
            cleanup()