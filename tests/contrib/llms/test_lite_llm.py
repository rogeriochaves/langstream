import json
import unittest
from typing import (
    List,
    Literal,
    TypedDict,
    Union,
)

import pytest

from langstream.core.stream import Stream
from langstream.contrib.llms.lite_llm import (
    LiteLLMChatDelta,
    LiteLLMChatMessage,
    LiteLLMChatStream,
)
from langstream.utils.stream import collect_final_output, debug


class LiteLLMChatStreamTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        stream = LiteLLMChatStream[str, LiteLLMChatDelta](
            "GreetingStream",
            lambda name: [
                LiteLLMChatMessage(role="user", content=f"Hello, my name is {name}")
            ],
            model="replicate/replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf",
            stream=False,
            temperature=0,
        )

        result = ""
        async for output in stream("Alice"):
            print(output.data.content, end="", flush=True)
            result += output.data.content
        self.assertIn("Hello Alice!", result)

    @pytest.mark.integration
    async def test_it_simulates_memory(self):
        class Memory(TypedDict):
            history: List[LiteLLMChatMessage]

        memory = Memory(history=[])

        def save_message_to_memory(message: LiteLLMChatMessage) -> LiteLLMChatMessage:
            memory["history"].append(message)
            return message

        def update_delta_on_memory(delta: LiteLLMChatDelta) -> LiteLLMChatDelta:
            if memory["history"][-1].role != delta.role and delta.role is not None:
                memory["history"].append(
                    LiteLLMChatMessage(role=delta.role, content=delta.content)
                )
            else:
                memory["history"][-1].content += delta.content
            return delta

        stream = debug(
            LiteLLMChatStream[str, LiteLLMChatDelta](
                "EmojiChatStream",
                lambda user_message: [
                    *memory["history"],
                    save_message_to_memory(
                        LiteLLMChatMessage(
                            role="user", content=f"{user_message}. Reply in emojis"
                        )
                    ),
                ],
                model="gpt-3.5-turbo",
                temperature=0,
            )
        ).map(update_delta_on_memory)

        outputs = await collect_final_output(
            stream("Hey there, my name is 🧨 how is it going?")
        )
        result = "".join([output.content for output in outputs])
        self.assertIn("👋🧨", result)

        outputs = await collect_final_output(stream("What is my name?"))
        result = "".join([output.content for output in outputs])
        self.assertIn("🧨", result)

        self.assertEqual(len(memory["history"]), 4)

    @pytest.mark.integration
    async def test_it_calls_simple_functions(self):
        class WeatherReturn(TypedDict):
            location: str
            forecast: str
            temperature: str

        def get_current_weather(
            location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
        ) -> WeatherReturn:
            return WeatherReturn(
                location=location,
                forecast="sunny",
                temperature="25 C" if format == "celsius" else "77 F",
            )

        stream: Stream[str, Union[LiteLLMChatDelta, WeatherReturn]] = debug(
            LiteLLMChatStream[str, LiteLLMChatDelta](
                "WeatherStream",
                lambda user_input: [
                    LiteLLMChatMessage(role="user", content=user_input),
                ],
                model="gpt-3.5-turbo",
                functions=[
                    {
                        "name": "get_current_weather",
                        "description": "Gets the current weather in a given location, use this function for any questions related to the weather",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "description": "The city to get the weather, e.g. San Francisco. Guess the location from user messages",
                                    "type": "string",
                                },
                                "format": {
                                    "description": "A string with the full content of what the given role said",
                                    "type": "string",
                                    "enum": ("celsius", "fahrenheit"),
                                },
                            },
                        },
                        "required": ["location"],
                    }
                ],
                temperature=0,
            ).map(
                lambda delta: get_current_weather(**json.loads(delta.content))
                if delta.role == "function" and delta.name == "get_current_weather"
                else delta
            )
        )

        outputs = await collect_final_output(
            stream(
                "I'm in my appartment in Amsterdam, thinking... should I take an umbrella for my pet chicken?"
            )
        )
        self.assertEqual(
            list(outputs)[0],
            {"location": "Amsterdam", "forecast": "sunny", "temperature": "25 C"},
        )

    @pytest.mark.integration
    async def test_it_keeps_function_calls_in_memory(self):
        class Memory(TypedDict):
            history: List[LiteLLMChatMessage]

        memory = Memory(history=[])

        class WeatherReturn(TypedDict):
            location: str
            forecast: str
            temperature: str

        def get_current_weather(
            location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
        ) -> LiteLLMChatDelta:
            result = WeatherReturn(
                location=location,
                forecast="sunny",
                temperature="25 C" if format == "celsius" else "77 F",
            )

            return LiteLLMChatDelta(
                role="function", name="get_current_weather", content=json.dumps(result)
            )

        def save_message_to_memory(message: LiteLLMChatMessage) -> LiteLLMChatMessage:
            memory["history"].append(message)
            return message

        def update_delta_on_memory(delta: LiteLLMChatDelta) -> LiteLLMChatDelta:
            if memory["history"][-1].role != delta.role and delta.role is not None:
                memory["history"].append(
                    LiteLLMChatMessage(
                        role=delta.role, content=delta.content, name=delta.name
                    )
                )
            else:
                memory["history"][-1].content += delta.content
            return delta

        stream = (
            debug(
                LiteLLMChatStream[str, LiteLLMChatDelta](
                    "WeatherStream",
                    lambda user_input: [
                        *memory["history"],
                        save_message_to_memory(
                            LiteLLMChatMessage(role="user", content=user_input),
                        ),
                    ],
                    model="gpt-3.5-turbo",
                    functions=[
                        {
                            "name": "get_current_weather",
                            "description": "Gets the current weather in a given location, use this function for any questions related to the weather",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "description": "The city to get the weather, e.g. San Francisco. Guess the location from user messages",
                                        "type": "string",
                                    },
                                    "format": {
                                        "description": "A string with the full content of what the given role said",
                                        "type": "string",
                                        "enum": ("celsius", "fahrenheit"),
                                    },
                                },
                            },
                            "required": ["location"],
                        }
                    ],
                    temperature=0,
                )
            )
            .map(
                lambda delta: get_current_weather(**json.loads(delta.content))
                if delta.role == "function" and delta.name == "get_current_weather"
                else delta
            )
            .map(update_delta_on_memory)
        )

        outputs = await collect_final_output(
            stream("What is the weather today in amsterdam?")
        )
        self.assertEqual(
            list(outputs)[0],
            LiteLLMChatDelta(
                role="function",
                content=json.dumps(
                    {
                        "location": "Amsterdam",
                        "forecast": "sunny",
                        "temperature": "25 C",
                    }
                ),
                name="get_current_weather",
            ),
        )

        outputs = await collect_final_output(stream("How many degrees again?"))
        result = "".join(
            [
                output.content
                for output in outputs
                if isinstance(output, LiteLLMChatDelta)
            ]
        )
        self.assertIn(
            "25 degrees",
            result,
        )
