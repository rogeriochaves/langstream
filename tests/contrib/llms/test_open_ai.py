import unittest
from typing import (
    Any,
    AsyncGenerator,
    List,
)

import pytest

from litechain.core.chain import Chain, ChainOutput
from litechain.utils.async_generator import as_async_generator
from litechain.contrib.llms.open_ai import OpenAICompletionChain


class OpenAITestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        chain = OpenAICompletionChain[str, str](
            "GreetingChain",
            lambda name: f"Human: Hello, my name is {name}\nAssistant: ",
            model="text-ada-001",
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
