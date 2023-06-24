import unittest
from typing import Iterable

from litechain.core.chain import Chain, SingleOutputChain
from litechain.utils.async_iterable import as_async_iterable, join


class ChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_chain = Chain[str, str](lambda input: f"{input}!")

        result = await join(exclamation_chain("hello world"))
        self.assertEqual(result, "hello world!")

    async def test_it_is_callable_with_async_iterable_return(self):
        exclamation_chain = Chain[str, str](lambda input: as_async_iterable(input, "!"))

        result = await join(exclamation_chain("hello world"))
        self.assertEqual(result, "hello world!")

    async def test_it_is_mappable(self):
        exclamation_chain = Chain[str, str](lambda input: f"{input}!")
        chain = exclamation_chain.map(lambda input: input.replace("world", "planet"))

        result = await join(chain("hello world"))
        self.assertEqual(result, "hello planet!")

    async def test_it_is_thenable(self):
        exclamation_stream_chain = Chain[str, str](
            lambda input: as_async_iterable(f"{input}", "!")
        )
        joiner_chain = Chain[Iterable[str], str](lambda input: ", ".join(input))

        chain = exclamation_stream_chain.and_then(joiner_chain)

        result = await join(chain("hello world"))
        self.assertEqual(result, "hello world, !")

    async def test_it_is_composable_by_waiting_the_first_chain_to_finish(self):
        hello_chain = Chain[str, str](lambda input: f"hello {input}")
        exclamation_chain = Chain[str, str](lambda input: f"{input}!")

        chain = hello_chain.join().and_then(exclamation_chain)

        result = await join(chain("world"))
        self.assertEqual(result, "hello world!")


class SingleOutputChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_chain = SingleOutputChain[str, str](lambda input: f"{input}!")

        result = await exclamation_chain("hello world")
        self.assertEqual(result, "hello world!")

    async def test_it_is_callable_with_async_return(self):
        async def async_exclamation(input: str):
            return f"{input}!"

        exclamation_chain = SingleOutputChain[str, str](
            lambda input: async_exclamation(input)
        )

        result = await exclamation_chain("hello world")
        self.assertEqual(result, "hello world!")
