from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.models import Model
from .prompt import agent_instruction
from .tools import test_tool

# Code Builder Agent
# Takes the original code and the review comments (read from state) and refactors the code.
test_runner_agent = LlmAgent(
    name="TestRunnerAgent",
    model=Model.GEMINI_2_0_FLASH,
    # Change 3: Improved instruction, correctly using state key injection
    instruction=agent_instruction,
    description="Execute unit tests generated from requirements.",
    output_key="test_result", # Stores output in state['build_result']
    tools=[
        test_tool
    ]
)
