from google.adk.agents import LlmAgent

from gen_code.common.models import Model
from gen_code.code_gen_agent.common.gen_file import generate_file_callback
from .prompt import agent_instruction
from .tools import build_source_code

# Code Builder Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_builder_agent = LlmAgent(
    name="CodeBuilderAgent",
    # model=Model.GEMINI_2_0_FLASH,
    # Change 3: Improved instruction, correctly using state key injection
    instruction=agent_instruction,
    description="Build code generated from requirements.",
    output_key="build_result", # Stores output in state['build_result']
    # Callback to build code from the output
    tools=[
        build_source_code
    ]
)
