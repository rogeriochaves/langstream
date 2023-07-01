import unittest
import asyncio
import random
import unittest
from typing import (
    Any,
    AsyncGenerator,
    Iterable,
    List,
    TypeVar,
    TypedDict,
    cast,
)

from litechain.core.chain import Chain, ChainOutput, SingleOutputChain
from litechain.utils.async_generator import as_async_generator, collect, next_item
from litechain.utils.chain import join_final_output

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


class ChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: f"{input}!"
        )

        result = await collect(exclamation_chain("hello world"))
        self.assertEqual(
            result,
            [ChainOutput(chain="ExclamationChain", output="hello world!", final=True)],
        )

    async def test_it_is_callable_with_async_iterable_return(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(input, "!")
        )

        result = await collect(exclamation_chain("hello world"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", output="hello world", final=True),
                ChainOutput(chain="ExclamationChain", output="!", final=True),
            ],
        )

    async def test_it_is_mappable_as_values_arrive(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(input, "!")
        )
        chain = exclamation_chain.map(
            lambda input: input.replace("world", "planet")
        ).map(lambda input: input + "~")

        result = await collect(chain("hello world"))
        self.assertEqual(
            result,
            [
                ChainOutput(
                    chain="ExclamationChain",
                    output="hello world",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map",
                    output="hello planet",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map@map",
                    output="hello planet~",
                    final=True,
                ),
                ChainOutput(
                    chain="ExclamationChain",
                    output="!",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map",
                    output="!",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map@map",
                    output="!~",
                    final=True,
                ),
            ],
        )

        result = await join_final_output(chain("hello world"))
        self.assertEqual(result, "hello planet~!~")

    async def test_it_is_thenable(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )
        chain = exclamation_chain.and_then(lambda input: ", ".join(input))

        result = await collect(chain("hello world"))
        self.assertEqual(
            result[-1],
            ChainOutput(
                chain="ExclamationChain@and_then",
                output="hello world, !",
                final=True,
            ),
        )

    async def test_it_is_thenable_with_single_value_return(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )

        chain = exclamation_chain.and_then(lambda input: ", ".join(input))

        result = await join_final_output(chain("hello world"))
        self.assertEqual(result, "hello world, !")

    async def test_it_gets_the_results_as_they_come(self):
        blocked = True

        async def block_for_flag(xs: Iterable[T]) -> AsyncGenerator[T, Any]:
            while blocked:
                pass
            for x in xs:
                yield x

        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )
        blocking_chain = Chain[Iterable[str], str]("BlockingChain", block_for_flag)
        JoinerChain = Chain[Iterable[str], str](
            "JoinerChain", lambda input: ", ".join(input)
        )

        chain = exclamation_chain.and_then(blocking_chain).and_then(JoinerChain)

        outputs = chain("hello world")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", output="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", output="!", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain", output="hello world, !", final=True),
        )

    async def test_it_is_composable_by_waiting_the_first_chain_to_finish(self):
        blocked = True

        async def block_for_flag(xs: Iterable[T]) -> AsyncGenerator[T, Any]:
            while blocked:
                pass
            for x in xs:
                yield x

        hello_chain = Chain[str, str](
            "HelloChain", lambda input: as_async_generator("hello ", input)
        )
        blocking_chain = Chain[Iterable[str], str]("BlockingChain", block_for_flag)
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: f"{input}!"
        )

        chain = hello_chain.and_then(blocking_chain).join().and_then(exclamation_chain)

        outputs = chain("world")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="HelloChain", output="hello ", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="HelloChain", output="world", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="BlockingChain@join", output="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", output="hello world!", final=True),
        )

    async def test_it_collects_the_outputs_to_a_list(self):
        chain: Chain[int, List[int]] = (
            Chain[int, int](
                "RangeChain", lambda start: as_async_generator(*range(start, 5))
            )
            .map(lambda input: input + 1)
            .collect()
        )

        outputs = chain(0)
        for i in range(0, 5):
            self.assertEqual(
                await next_item(outputs),
                ChainOutput(chain="RangeChain", output=i, final=False),
            )
            self.assertEqual(
                await next_item(outputs),
                ChainOutput(chain="RangeChain@map", output=i + 1, final=False),
            )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="RangeChain@map@collect", output=[1, 2, 3, 4, 5], final=True
            ),
        )

    async def test_it_can_process_many_things_in_parallel(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        chain: Chain[int, str] = (
            Chain[int, int](
                "ParallelChain", lambda start: as_async_generator(*range(start, 100))
            )
            .map(increment_number)
            .collect()
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        outputs = chain(0)

        for i in range(0, 100):
            self.assertEqual(
                await next_item(outputs),
                ChainOutput(chain="ParallelChain", output=i, final=False),
            )
            self.assertIsInstance(
                (await next_item(outputs)).output,
                AsyncGenerator,
            )
        collect_next = await next_item(outputs)
        self.assertEqual(len(cast(List, collect_next.output)), 100)
        self.assertIsInstance(
            cast(List, collect_next.output)[0],
            AsyncGenerator,
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather",
                output=[[i + 1] for i in range(0, 100)],
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather@and_then",
                output=5050,
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather@and_then@map",
                output="5050",
                final=True,
            ),
        )

    async def test_it_can_gather_chain_mappings(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        inc_chain = SingleOutputChain[int, int]("IncChain", increment_number)

        chain: Chain[int, str] = (
            Chain[int, int](
                "ParallelChain", lambda start: as_async_generator(*range(start, 100))
            )
            .map(inc_chain)
            .collect()
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        result = await join_final_output(chain(0))
        self.assertEqual(result, "5050")

    async def test_it_can_gather_direclty_from_the_chain(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        chain: Chain[int, str] = (
            Chain[int, int](
                "ParallelChain", lambda start: as_async_generator(*range(start, 100))
            )
            .map(increment_number)
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        result = await join_final_output(chain(0))
        self.assertEqual(result, "5050")

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
            "GreetingChain",
            lambda input: "how are you?"
            if "hello" in memory["history"]
            else f"hello {input}",
        ).map(save_to_memory)

        result = await join_final_output(chain("José"))
        self.assertEqual(result, "hello José")

        result = await join_final_output(chain("hello"))
        self.assertEqual(result, "how are you?")


class SingleOutputChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_chain = SingleOutputChain[str, str](
            "ExclamationChain", lambda input: f"{input}!"
        )

        outputs = exclamation_chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", output="hello world!", final=True),
        )

    @unittest.skip("TODO")
    async def test_it_is_callable_with_async_return(self):
        async def async_exclamation(input: str):
            return f"{input}!"

        exclamation_chain = SingleOutputChain[str, str](
            "ExclamationChain", lambda input: async_exclamation(input)  # type: ignore (TODO)
        )

        result = await join_final_output(exclamation_chain("hello world"))
        self.assertEqual(result, "hello world!")

    async def test_it_is_thenable_keeping_the_proper_chain_names(self):
        exclamation_list_chain = SingleOutputChain[str, List[str]](
            "ExclamationListChain", lambda input: [f"{input}", "!"]
        )
        joiner_chain = Chain[Iterable[str], str](
            "JoinerChain", lambda input: ", ".join(input)
        )

        chain = exclamation_list_chain.and_then(joiner_chain).map(
            lambda input: input + "~"
        )

        outputs = chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain", output=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain", output="hello world, !", final=False),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain@map", output="hello world, !~", final=True),
        )

    async def test_it_is_thenable_with_single_value_return(self):
        exclamation_list_chain = SingleOutputChain[str, List[str]](
            "ExclamationListChain", lambda input: [f"{input}", "!"]
        )

        chain = exclamation_list_chain.and_then(lambda input: ", ".join(input))

        outputs = chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain", output=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@and_then",
                output="hello world, !",
                final=True,
            ),
        )
