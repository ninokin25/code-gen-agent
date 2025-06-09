import unittest
from src.gen_code.weather_agent.agent import weather_agent, AGENT_MODEL
from src.gen_code.weather_agent import tools

class TestWeatherAgent(unittest.TestCase):

    def test_agent_creation(self):
        """Test that the weather_agent object is created."""
        self.assertIsNotNone(weather_agent)

    def test_agent_name(self):
        """Test the agent's name is correctly set."""
        self.assertEqual(weather_agent.name, "weather_agent_v1")

    def test_agent_model(self):
        """Test the agent's model is correctly set."""
        self.assertEqual(weather_agent.model, AGENT_MODEL)
        # Also check if the AGENT_MODEL is one of the predefined ones, e.g.
        # self.assertIn(AGENT_MODEL, [MODEL_GEMINI_2_0_FLASH, MODEL_CLAUDE_SONNET, MODEL_GEMINI_2_5_PRO])
        # However, these constants are not directly exported by the agent.py for this test.
        # For simplicity, we'll just check against the imported AGENT_MODEL.

    def test_agent_description(self):
        """Test the agent's description is correctly set."""
        self.assertEqual(weather_agent.description, "Provides weather information for specific cities.")

    def test_agent_instruction(self):
        """Test the agent's instruction is correctly set."""
        expected_instruction = (
            "You are a helpful weather assistant. Your primary goal is to provide current weather reports. "
            "When the user asks for the weather in a specific city, "
            "you MUST use the 'get_weather' tool to find the information. "
            "Analyze the tool's response: if the status is 'error', inform the user politely about the error message. "
            "If the status is 'success', present the weather 'report' clearly and concisely to the user. "
            "Only use the tool when a city is mentioned for a weather request."
        )
        self.assertEqual(weather_agent.instruction, expected_instruction)

    def test_agent_tools(self):
        """Test the agent's tools list is correctly set."""
        self.assertIsInstance(weather_agent.tools, list)
        self.assertEqual(len(weather_agent.tools), 1)
        self.assertIs(weather_agent.tools[0], tools.get_weather)

if __name__ == '__main__':
    unittest.main()
