import unittest
from typing import Any, AsyncGenerator, List

import pytest

from langstream import Stream, StreamOutput, as_async_generator, debug, join_final_output
from langstream.contrib.llms.gpt4all_stream import GPT4AllStream


class GPT4AllStreamTestCase(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.integration
    async def test_it_completes_a_simple_prompt(self):
        stream = debug(
            GPT4AllStream[str, str](
                "GreetingStream",
                lambda name: f"### User: Hello, my name is {name}. How is it going?\n\n### Response:",
                model="orca-mini-3b-gguf2-q4_0.gguf",
                temperature=0,
            )
        )

        result = await join_final_output(stream("Alice"))
        self.assertIn("I'm doing well, thank you for asking!", result)

    @pytest.mark.integration
    @pytest.mark.skip(
        "parallelization will not work with GPT4All because we create only one instance for it in the main thread and don't multiply memory, this is probably what users will want too to use all the cores, so skipping this for now"
    )
    async def test_it_is_non_blocking(self):
        async_stream = GPT4AllStream[str, str](
            "AsyncStream",
            lambda _: f"to make a function asynchronous in js, use the keyword `",
            model="orca-mini-3b-gguf2-q4_0.gguf",
            max_tokens=2,
            temperature=0,
        )

        parallel_stream: Stream[str, List[List[str]]] = Stream[
            str, AsyncGenerator[StreamOutput[str, Any], None]
        ](
            "ParallelStream",
            lambda input: as_async_generator(
                async_stream(input),
                async_stream(input),
                async_stream(input),
                async_stream(input),
            ),
        ).gather()

        async for output in parallel_stream("Alice"):
            if isinstance(output.data, str):
                print(output.data)
            if output.final:
                self.assertEqual(
                    output.data,
                    [
                        ["as", "ync"],
                        ["as", "ync"],
                        ["as", "ync"],
                        ["as", "ync"],
                    ],
                )
