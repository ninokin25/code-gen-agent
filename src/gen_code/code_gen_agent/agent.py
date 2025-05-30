from google.adk.agents import SequentialAgent

from .code_writer_agent.agent import code_writer_agent
from .code_reviewer_agent.agent import code_reviewer_agent
from .code_refactorer_agent.agent import code_refactorer_agent

# This agent orchestrates the pipeline by running the sub_agents in order.
# code_pipeline_agent = SequentialAgent(
root_agent  = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[
        code_writer_agent,
        code_reviewer_agent,
        code_refactorer_agent
    ],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)
