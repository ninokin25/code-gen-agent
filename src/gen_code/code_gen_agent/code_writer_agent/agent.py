from google.adk.agents import LlmAgent

from gen_code.common.models import Model
from gen_code.code_gen_agent.common.gen_file import generate_file_callback
from .prompt import agent_instruction

# Code Writer Agent
# Takes the initial specification (from user query) and writes code.
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model=Model.GEMINI_2_0_FLASH.value,
    # Change 3: Improved instruction
    instruction=agent_instruction,
    description="Writes initial Python code based on a specification.",
    output_key="generated_code", # Stores output in state['generated_code']
    after_agent_callback=generate_file_callback
)
