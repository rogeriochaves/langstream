import unittest
from typing import Iterable

from lightchain.core.chain import Chain, Response
from lightchain.utils.async_iterable import join


class ChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable(self):
        exclamation_chain = Chain[str, str](lambda input: Response.of(f"{input}!"))

        result = await join(exclamation_chain("hello world"))
        self.assertEqual(result, "hello world!")

    async def test_it_is_mappable(self):
        exclamation_chain = Chain[str, str](lambda input: Response.of(f"{input}!"))
        chain = exclamation_chain.map(lambda input: input.replace("world", "planet"))

        result = await join(chain("hello world"))
        self.assertEqual(result, "hello planet!")

    async def test_it_is_thenable(self):
        exclamation_stream_chain = Chain[str, str](
            lambda input: Response.of(f"{input}", "!")
        )
        joiner_chain = Chain[Iterable[str], str](
            lambda input: Response.of(", ".join(input))
        )

        chain = exclamation_stream_chain.and_then(joiner_chain)

        result = await join(chain("hello world"))
        self.assertEqual(result, "hello world, !")

    async def test_it_is_composable_by_waiting_the_first_chain_to_finish(self):
        hello_chain = Chain[str, str](lambda input: Response.of(f"hello {input}"))
        exclamation_chain = Chain[str, str](lambda input: Response.of(f"{input}!"))

        chain = hello_chain.join().and_then(exclamation_chain)

        result = await join(chain("world"))
        self.assertEqual(result, "hello world!")
