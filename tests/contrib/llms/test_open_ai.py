import unittest
from typing import (
    Any,
    AsyncGenerator,
    List,
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


class OpenAICompletionChainTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        chain = OpenAICompletionChain[str, str](
            "GreetingChain",
            lambda name: f"Human: Hello, my name is {name}\nAssistant: ",
            model="text-ada-001",
            temperature=0,
        )

        result = ""
        async for output in chain("Alice"):
            print(output.output, end="", flush=True)
            result += output.output
        self.assertIn("I am an assistant", result)

    @pytest.mark.integration
    @pytest.mark.timeout(
        0.7  # if due to some bug it ends up being blocking, then it will break this threshold
    )
    async def test_it_is_non_blocking(self):
        async_chain = OpenAICompletionChain[str, str](
            "AsyncChain",
            lambda _: f"Say async. Assistant: \n",
            model="text-ada-001",
            max_tokens=2,
            temperature=0,
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

        async for output in parallel_chain("Alice"):
            if isinstance(output.output, str):
                print(output.output)
            if output.final:
                self.assertEqual(
                    output.output,
                    [
                        ["\n", "Async"],
                        ["\n", "Async"],
                        ["\n", "Async"],
                        ["\n", "Async"],
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
            print(output.output["content"], end="", flush=True)
            result += output.output["content"]
        self.assertIn("Hello Alice! How can I assist you today?", result)
