from google.adk.agents import LlmAgent

from gen_code.common.models import Model
from .prompt import agent_instruction
from .tools import build_tool

# Code Builder Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_builder_agent = LlmAgent(
    name="CodeBuilderAgent",
    model=Model.GEMINI_2_0_FLASH,
    # Change 3: Improved instruction, correctly using state key injection
    instruction=agent_instruction,
    description="Build code generated from requirements.",
    output_key="build_result", # Stores output in state['build_result']
    tools=[
        build_tool
    ]
)
