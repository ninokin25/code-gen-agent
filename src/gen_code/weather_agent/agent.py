import os
import asyncio
from google.adk.agents import Agent
from . import tools


MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_GEMINI_2_5_PRO = "gemini-2.5-pro-exp-03-25"

AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL,
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. Your primary goal is to provide current weather reports. "
                "When the user asks for the weather in a specific city, "
                "you MUST use the 'get_weather' tool to find the information. "
                "Analyze the tool's response: if the status is 'error', inform the user politely about the error message. "
                "If the status is 'success', present the weather 'report' clearly and concisely to the user. "
                "Only use the tool when a city is mentioned for a weather request.",
    tools=[tools.get_weather], # Toolリスト
)
