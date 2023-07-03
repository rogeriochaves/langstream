import unittest
from typing import Any, AsyncGenerator, List

import pytest

from litechain import Chain, ChainOutput, as_async_generator, debug, join_final_output
from litechain.contrib.llms.gpt4all_chain import GPT4AllChain


class GPT4AllChainTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        chain = debug(
            GPT4AllChain[str, str](
                "GreetingChain",
                lambda name: f"### User: Hello, my name is {name}. How is it going?\n\n### Response:",
                model="orca-mini-3b.ggmlv3.q4_0.bin",
                temperature=0,
            )
        )

        result = await join_final_output(chain("Alice"))
        self.assertIn("I'm doing well, thank you for asking!", result)

    @pytest.mark.integration
    @pytest.mark.skip(
        "parallelization will not work with GPT4All because we create only one instance for it in the main thread and don't multiply memory, this is probably what users will want too to use all the cores, so skipping this for now"
    )
    async def test_it_is_non_blocking(self):
        async_chain = GPT4AllChain[str, str](
            "AsyncChain",
            lambda _: f"to make a function asynchronous in js, use the keyword `",
            model="orca-mini-3b.ggmlv3.q4_0.bin",
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
                        ["as", "ync"],
                        ["as", "ync"],
                        ["as", "ync"],
                        ["as", "ync"],
                    ],
                )
