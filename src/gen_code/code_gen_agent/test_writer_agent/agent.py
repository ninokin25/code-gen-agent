from google.adk.agents import LlmAgent

from gen_code.code_gen_agent.common.models import Model
from .tools import generate_test_callback
from .prompt import agent_instruction

# Test Writer Agent
# Generates GoogleTest-based unit tests for C code, and writes the test file.
test_writer_agent = LlmAgent(
    name="TestWriterAgent",
    model=Model.GEMINI_2_0_FLASH.value,
    instruction=agent_instruction,
    description="Generates GoogleTest (gtest) unit tests for C code based on the provided source and header files, and writes the test code to a .cpp file.",
    output_key="generated_test_code",  # Stores output in state['generated_test_code']
    after_agent_callback=generate_test_callback
)
