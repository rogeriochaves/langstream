import unittest
from typing import (
    Any,
    AsyncGenerator,
    List,
    TypedDict,
)

import pytest

from litechain.core.chain import Chain, ChainOutput
from litechain.utils.async_generator import as_async_generator
from litechain.contrib.llms.open_ai import (
    OpenAIChatDelta,
    OpenAIChatMessage,
    OpenAICompletionChain,
    OpenAIChatChain,
)
from litechain.utils.chain import collect_final_output, debug, join_final_output


class OpenAICompletionChainTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        chain = debug(
            OpenAICompletionChain[str, str](
                "GreetingChain",
                lambda name: f"Human: Hello, my name is {name}\nAssistant: ",
                model="text-ada-001",
                temperature=0,
            )
        )

        result = await join_final_output(chain("Alice"))
        self.assertIn("I am an assistant", result)

    @pytest.mark.integration
    @pytest.mark.timeout(
        0.7  # if due to some bug it ends up being blocking, then it will break this threshold
    )
    async def test_it_is_non_blocking(self):
        async_chain = debug(
            OpenAICompletionChain[str, str](
                "AsyncChain",
                lambda _: f"Say async. Assistant: \n",
                model="text-ada-001",
                max_tokens=2,
                temperature=0,
            )
        )

        parallel_chain: Chain[str, List[List[str]]] = Chain[
            str, AsyncGenerator[ChainOutput[str, Any], None]
        ](
            "ParallelChain",
            lambda input: as_async_generator(
                async_chain(input),
                async_chain(input),
                async_chain(input),
                async_chain(input),
            ),
        ).gather()

        result = await collect_final_output(parallel_chain("Alice"))
        self.assertEqual(
            result,
            [
                [
                    ["\n", "Async"],
                    ["\n", "Async"],
                    ["\n", "Async"],
                    ["\n", "Async"],
                ]
            ],
        )


class OpenAIChatChainTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        chain = OpenAIChatChain[str, OpenAIChatDelta](
            "GreetingChain",
            lambda name: [
                OpenAIChatMessage(role="user", content=f"Hello, my name is {name}")
            ],
            model="gpt-3.5-turbo-0613",
            temperature=0,
        )

        result = ""
        async for output in chain("Alice"):
            print(output.data.content, end="", flush=True)
            result += output.data.content
        self.assertIn("Hello Alice! How can I assist you today?", result)

    @pytest.mark.integration
    async def test_it_simulates_memory(self):
        class Memory(TypedDict):
            history: List[OpenAIChatMessage]

        memory = Memory(history=[])

        def save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:
            memory["history"].append(message)
            return message

        def update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:
            if memory["history"][-1].role != delta.role and delta.role is not None:
                memory["history"].append(
                    OpenAIChatMessage(role=delta.role, content=delta.content)
                )
            else:
                memory["history"][-1].content += delta.content
            return delta

        chain = debug(
            OpenAIChatChain[str, OpenAIChatDelta](
                "EmojiChatChain",
                lambda user_message: [
                    *memory["history"],
                    save_message_to_memory(
                        OpenAIChatMessage(
                            role="user", content=f"{user_message}. Reply in emojis"
                        )
                    ),
                ],
                model="gpt-3.5-turbo-0613",
                temperature=0,
            )
        ).map(update_delta_on_memory)

        outputs = await collect_final_output(
            chain("Hey there, my name is 🧨 how is it going?")
        )
        result = "".join([output.content for output in outputs])
        self.assertIn("👋🧨", result)

        outputs = await collect_final_output(chain("What is my name?"))
        result = "".join([output.content for output in outputs])
        self.assertIn("🧨", result)

        self.assertEqual(len(memory["history"]), 4)
