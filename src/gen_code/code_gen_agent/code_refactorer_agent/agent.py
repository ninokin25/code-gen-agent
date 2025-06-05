from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.config import AGENT_MODELS
from gen_code.code_gen_agent.common.gen_file import generate_file_callback
from .prompt import agent_instruction

# Code Refactorer Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model=AGENT_MODELS['default'], # Model sourced from common.config
    instruction=agent_instruction,
    description="Refactors code based on review comments.",
    output_key="refactored_code",
    after_agent_callback=generate_file_callback
)
