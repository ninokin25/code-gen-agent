"""
Centralized configuration for code generation agents.

This file stores common settings such as Large Language Model (LLM) names,
default iteration limits for loop agents, and other shared parameters
to ensure consistency and ease of modification across the agent framework.
"""
from .models import Model

# Defines the LLM models to be used by different agents or roles.
# 'default' is used by most agents unless a specific role (e.g., 'code_reviewer')
# is assigned a different model.
AGENT_MODELS = {
    'default': Model.GEMINI_2_0_FLASH.value,  # Default model for general agent tasks.
    'code_reviewer': Model.GEMINI_1_5_PRO.value,  # Potentially a more powerful model for review tasks.
    # Example: 'code_writer': Model.GEMINI_1_5_PRO.value, # If writer needs a different model
}

# --- Specific Model Strings ---
# These provide direct access to model name strings. Some agents or parts of the
# framework might use these directly instead of or in addition to AGENT_MODELS.

# Gemini 2.0 Flash model, often used for its balance of speed and capability.
# Referenced by weather_agent and potentially others requiring this specific version.
MODEL_GEMINI_2_0_FLASH = Model.GEMINI_2_0_FLASH.value

# Claude 3 Sonnet model by Anthropic.
# Used as an alternative model, for example, in weather_agent.
MODEL_CLAUDE_SONNET = "claude-3-sonnet-20240229" # String literal as per original definition

# Gemini 1.5 Pro model (latest version).
# Used as an alternative or for more demanding tasks.
# Note: The original mapping was to GEMINI_1_5_PRO, which is now correctly reflected.
MODEL_GEMINI_2_5_PRO = Model.GEMINI_1_5_PRO.value

# --- Loop Agent Configurations ---

# Default maximum number of iterations for LoopAgents within the framework.
# This helps prevent infinite loops and controls the extent of refinement cycles.
DEFAULT_MAX_ITERATIONS = 5

# Example of more specific iteration counts (can be added if needed):
# CODE_REFINEMENT_MAX_ITERATIONS = 5 # For loops focusing on code refinement.
# TEST_REFINEMENT_MAX_ITERATIONS = 3  # For loops focusing on test generation/refinement.

# --- Weather Agent Specific Model Organization (Optional Example) ---
# If model organization per agent group is preferred, a dictionary like this can be used:
# WEATHER_AGENT_MODELS = {
#     'flash': MODEL_GEMINI_2_0_FLASH, # Accessing the constant defined above
#     'sonnet': MODEL_CLAUDE_SONNET,
#     'pro': MODEL_GEMINI_2_5_PRO,
# }
