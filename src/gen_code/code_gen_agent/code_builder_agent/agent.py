from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.config import AGENT_MODELS
from .prompt import agent_instruction
from .tools import build_tool

# Code Builder Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_builder_agent = LlmAgent(
    name="CodeBuilderAgent",
    model=AGENT_MODELS['default'], # Model sourced from common.config
    instruction=agent_instruction,
    description="Build code generated from requirements.",
    output_key="build_result",
    tools=[
        build_tool
    ]
)
