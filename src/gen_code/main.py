from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from gen_code.weather_agent.agent import weather_agent

import asyncio
from google.genai import types

from dotenv import load_dotenv
import logging
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
load_dotenv()

session_service = InMemorySessionService()

APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

runner = Runner(
    agent=weather_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner created for agent '{runner.agent.name}'.")

async def call_agent_async(query: str, user_id: str, session_id: str):
  print(f"\n>>> User Query: {query}")
  content = types.Content(role='user', parts=[types.Part(text=query)])
  final_response_text = "Agent did not produce a final response."

  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      if event.is_final_response():
          if event.content and event.content.parts:
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate:
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          break

  print(f"<<< Agent Response: {final_response_text}")
  return final_response_text

async def run_conversation(user_id: str, session_id: str):
    await call_agent_async("ロンドンの天気は?", user_id, session_id)
    await call_agent_async("パリについては？", user_id, session_id)
    await call_agent_async("ニューヨークの天気を教えて下さい。", user_id, session_id)

async def main():
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    await run_conversation(USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(main())
