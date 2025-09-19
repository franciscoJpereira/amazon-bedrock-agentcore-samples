from strands import Agent, tool
from strands_tools import calculator # Import the calculator tool
import argparse
import json
import asyncio
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# Create a custom tool 
@tool
def weather():
    """ Get weather data as a simple string denoting 
        if it is sunny, cloudy, rainy, cold or hot.   
    """ # Dummy implementation
    return "sunny"




model_id = "anthropic.claude-3-haiku-20240307-v1:0"
model = BedrockModel(
    model_id=model_id,
)
agent = Agent(
    model=model,
    tools=[calculator, weather],
    system_prompt="You're a helpful assistant. You can do simple math calculation, and tell the weather."
)

@app.entrypoint
async def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    try:
        async for event in agent.stream_async(user_input):
            if "data" in event:
                yield event["data"]
    except Exception as e:
        error_response = {
            "error": str(e), "type": "stream_error"
        }
        print(f"Streaming error: {error_response}")
        yield error_response
        
if __name__ == "__main__":
    app.run()