from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.models import Model
from .prompt import agent_instruction
from .tools import build_tool

# Code Builder Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_builder_agent = LlmAgent(
    name="CodeBuilderAgent",
    model=Model.GEMINI_2_0_FLASH,
    instruction=agent_instruction,
    description="Build code generated from requirements.",
    output_key="build_result",
    tools=[
        build_tool
    ]
)
