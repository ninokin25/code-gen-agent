import os
import asyncio
from google.adk.agents import Agent
from . import tools
from gen_code.code_gen_agent.common.config import MODEL_GEMINI_2_0_FLASH, MODEL_CLAUDE_SONNET, MODEL_GEMINI_2_5_PRO


weather_agent = Agent(
    name="weather_agent_v1",
    model=MODEL_GEMINI_2_0_FLASH, # Model string sourced from gen_code.code_gen_agent.common.config
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. Your primary goal is to provide current weather reports. "
                "When the user asks for the weather in a specific city, "
                "you MUST use the 'get_weather' tool to find the information. "
                "Analyze the tool's response: if the status is 'error', inform the user politely about the error message. "
                "If the status is 'success', present the weather 'report' clearly and concisely to the user. "
                "Only use the tool when a city is mentioned for a weather request.",
    tools=[tools.get_weather], # Toolリスト
)
