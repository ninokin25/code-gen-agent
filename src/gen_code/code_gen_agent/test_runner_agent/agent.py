from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.config import AGENT_MODELS
from .prompt import agent_instruction
from .tools import test_tool

# Test Runner Agent
# Executes unit tests and processes the results.
test_runner_agent = LlmAgent(
    name="TestRunnerAgent",
    model=AGENT_MODELS['default'], # Model sourced from common.config
    # Change 3: Improved instruction, correctly using state key injection
    instruction=agent_instruction,
    description="Execute unit tests generated from requirements.",
    output_key="test_result", # Stores output in state['test_result']
    tools=[
        test_tool
    ]
)
