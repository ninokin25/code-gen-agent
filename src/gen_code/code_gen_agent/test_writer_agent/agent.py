from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.config import AGENT_MODELS
from gen_code.code_gen_agent.common.callback_utils import generate_test_callback # Updated import
from .prompt import agent_instruction

# Test Writer Agent
# Generates GoogleTest-based unit tests for C code, and writes the test file.
test_writer_agent = LlmAgent(
    name="TestWriterAgent",
    model=AGENT_MODELS['default'], # Model sourced from common.config
    instruction=agent_instruction,
    description="Generates GoogleTest (gtest) unit tests for C code based on the provided source and header files, and writes the test code to a .cpp file.",
    output_key="generated_test_code",  # Stores output in state['generated_test_code']
    after_agent_callback=generate_test_callback
)
