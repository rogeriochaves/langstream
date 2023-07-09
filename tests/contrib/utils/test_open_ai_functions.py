import unittest
from typing import Literal

from litechain.contrib.utils.open_ai_functions import py2gpt


class OpenAIFunctionsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_completes_a_simple_prompt(self):
        def get_current_weather(
            location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
        ):
            """
            Gets the current weather in a given location, use this function for any questions related to the weather"

            Attributes
            ----------
            location
                The city to check for the weather

            format
                Unit for formatting the temperature
            """

            return "sunny"

        spec = py2gpt(get_current_weather)
        self.assertEqual(
            spec,
            {
                "name": "get_current_weather",
                "description": 'Gets the current weather in a given location, use this function for any questions related to the weather"',
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "description": "The city to check for the weather",
                            "type": "string",
                        },
                        "format": {
                            "description": "Unit for formatting the temperature",
                            "type": "string",
                            "enum": ("celsius", "fahrenheit"),
                        },
                    },
                },
                "required": ["location"],
            },
        )
