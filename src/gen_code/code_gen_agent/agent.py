from google.adk.agents import LoopAgent, SequentialAgent

from .code_writer_agent.agent import code_writer_agent
from .code_reviewer_agent.agent import code_reviewer_agent
from .code_refactorer_agent.agent import code_refactorer_agent
from .code_builder_agent.agent import code_builder_agent
from .test_writer_agent.agent import test_writer_agent
from .test_runner_agent.agent import test_runner_agent
from .common.config import DEFAULT_MAX_ITERATIONS

code_refinement_loop = LoopAgent(
    name="CodeRefinementLoop",
    # Agent order is crucial: Review First, then refactoring and build code.
    sub_agents=[
        code_reviewer_agent,
        code_refactorer_agent,
        code_builder_agent,
    ],
    max_iterations=DEFAULT_MAX_ITERATIONS # Max iterations sourced from common.config
)

test_refinement_loop = LoopAgent(
    name="TestRefinementLoop",
    # Agent order is crucial: Write tests First, then executing tests.
    sub_agents=[
        test_writer_agent,
        test_runner_agent,
    ],
    max_iterations=DEFAULT_MAX_ITERATIONS # Max iterations sourced from common.config
)

root_agent  = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[
        code_writer_agent,
        code_refinement_loop,
        test_refinement_loop
    ],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer -> Builder -> Test Writer
)
