import asyncio
import random
import unittest
from typing import Iterable, TypedDict

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

    async def test_it_is_thenable_with_single_value_return(self):
        exclamation_stream_chain = Chain[str, str](
            lambda input: as_async_iterable(f"{input}", "!")
        )

        chain = exclamation_stream_chain.and_then(lambda input: ", ".join(input))

        result = await join(chain("hello world"))
        self.assertEqual(result, "hello world, !")

    async def test_it_is_composable_by_waiting_the_first_chain_to_finish(self):
        hello_chain = Chain[str, str](lambda input: f"hello {input}")
        exclamation_chain = Chain[str, str](lambda input: f"{input}!")

        chain = hello_chain.join().and_then(exclamation_chain)

        result = await join(chain("world"))
        self.assertEqual(result, "hello world!")

    async def test_it_uses_a_simple_dict_as_memory(
        self,
    ):
        class Memory(TypedDict):
            history: str

        def save_to_memory(token: str):
            memory["history"] += token
            return token

        memory = Memory(history="")

        chain = Chain[str, str](
            lambda input: "how are you?"
            if "hello" in memory["history"]
            else f"hello {input}"
        ).map(save_to_memory)

        result = await join(chain("José"))
        self.assertEqual(result, "hello José")

        result = await join(chain("hello"))
        self.assertEqual(result, "how are you?")

    async def test_it_can_process_many_things_in_parallel(self):
        async def increment_number(num: int) -> int:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            return num + 1

        chain: Chain[int, str] = (
            Chain[int, int](lambda _: as_async_iterable(*range(0, 100)))
            .map(increment_number)
            .collect()
            .gather()
            .and_then(lambda result: sum(result))
            .map(lambda x: str(x))
        )

        result = await join(chain(0))
        self.assertEqual(result, "5050")


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

    # TODO: should be SingleOutputChain, accept both actually
    # async def test_it_is_thenable(self):
    #     exclamation_stream_chain = SingleOutputChain[str, List[str]](
    #         lambda input: [f"{input}", "!"]
    #     )
    #     joiner_chain = SingleOutputChain[Iterable[str], str](lambda input: ", ".join(input))

    #     chain = exclamation_stream_chain.and_then(joiner_chain)

    #     result = await join(chain("hello world"))
    #     self.assertEqual(result, "hello world, !")

    # async def test_it_is_thenable_with_single_value_return(self):
    #     exclamation_stream_chain = SingleOutputChain[str, List[str]](
    #         lambda input: [f"{input}", "!"]
    #     )

    #     chain = exclamation_stream_chain.and_then(lambda input: ", ".join(input))

    #     result = await join(chain("hello world"))
    #     self.assertEqual(result, "hello world, !")
