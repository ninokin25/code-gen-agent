import unittest
from src.gen_code.weather_agent.tools import get_weather

class TestWeatherTools(unittest.TestCase):

    def test_get_weather_success_new_york(self):
        """Test successful weather retrieval for New York."""
        result = get_weather("New York")
        self.assertEqual(result["status"], "success")
        self.assertIn("New York is sunny", result["report"])
        self.assertNotIn("error_message", result)

    def test_get_weather_success_london(self):
        """Test successful weather retrieval for London."""
        result = get_weather("London")
        self.assertEqual(result["status"], "success")
        self.assertIn("cloudy in London", result["report"])
        self.assertNotIn("error_message", result)

    def test_get_weather_success_tokyo(self):
        """Test successful weather retrieval for Tokyo."""
        result = get_weather("Tokyo")
        self.assertEqual(result["status"], "success")
        self.assertIn("Tokyo is experiencing light rain", result["report"])
        self.assertNotIn("error_message", result)

    def test_get_weather_success_case_insensitivity(self):
        """Test that city names are handled case-insensitively."""
        result_upper = get_weather("NEW YORK")
        self.assertEqual(result_upper["status"], "success")
        self.assertIn("New York is sunny", result_upper["report"])

        result_lower = get_weather("london")
        self.assertEqual(result_lower["status"], "success")
        self.assertIn("cloudy in London", result_lower["report"])

    def test_get_weather_success_space_handling(self):
        """Test that spaces in city names are handled."""
        # The current implementation normalizes spaces by removing them.
        # "new york" becomes "newyork"
        result = get_weather("New York") # Already tested, but good for clarity
        self.assertEqual(result["status"], "success")

        # Depending on how strict we want to be, we might add a city with a space
        # in the mock_weather_db for a more direct test, e.g. "san francisco".
        # For now, we rely on the existing normalization.
        # If "new york" (with space) was a key in mock_weather_db, this would be different.
        # This test currently re-affirms existing behavior.

    def test_get_weather_error_unknown_city(self):
        """Test error handling for an unknown city."""
        city = "UnknownCity"
        result = get_weather(city)
        self.assertEqual(result["status"], "error")
        self.assertIn(f"don't have weather information for '{city}'", result["error_message"])
        self.assertNotIn("report", result)

    def test_get_weather_error_another_unknown_city(self):
        """Test error handling for another unknown city."""
        city = "Paris" # Assuming Paris is not in the mock DB
        result = get_weather(city)
        self.assertEqual(result["status"], "error")
        self.assertIn(f"don't have weather information for '{city}'", result["error_message"])
        self.assertNotIn("report", result)

if __name__ == '__main__':
    unittest.main()
