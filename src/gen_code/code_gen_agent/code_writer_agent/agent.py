from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.config import AGENT_MODELS
from gen_code.code_gen_agent.common.gen_file import generate_file_callback
from .prompt import agent_instruction

# Code Writer Agent
# Takes the initial specification (from user query) and writes code.
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model=AGENT_MODELS['default'], # Model sourced from common.config
    instruction=agent_instruction,
    description="Writes initial C code based on a specification.",
    output_key="generated_code",
    after_agent_callback=generate_file_callback
)
