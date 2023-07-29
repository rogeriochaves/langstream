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
            [ChainOutput(chain="ExclamationChain", data="hello world!", final=True)],
        )

    async def test_it_is_callable_with_async_iterable_return(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(input, "!")
        )

        result = await collect(exclamation_chain("hello world"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", data="hello world", final=True),
                ChainOutput(chain="ExclamationChain", data="!", final=True),
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
                    data="hello world",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map",
                    data="hello planet",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map@map",
                    data="hello planet~",
                    final=True,
                ),
                ChainOutput(
                    chain="ExclamationChain",
                    data="!",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map",
                    data="!",
                    final=False,
                ),
                ChainOutput(
                    chain="ExclamationChain@map@map",
                    data="!~",
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
                data="hello world, !",
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

    async def test_it_is_pipeable(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )

        async def upper_pipe(stream):
            async for value in stream:
                yield value.upper()

        chain: Chain[str, str] = exclamation_chain.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(chain("Hello World"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", data="Hello World", final=False),
                ChainOutput(
                    chain="ExclamationChain@map", data="hello world", final=False
                ),
                ChainOutput(
                    chain="ExclamationChain@map@pipe", data="HELLO WORLD", final=True
                ),
                ChainOutput(chain="ExclamationChain", data="!", final=False),
                ChainOutput(chain="ExclamationChain@map@pipe", data="!", final=True),
                ChainOutput(chain="ExclamationChain@map", data="!", final=False),
            ],
        )

    async def test_it_is_pipeable_with_a_delay_on_producer(self):
        async def exclamation_output(input) -> AsyncGenerator[str, Any]:
            yield input
            await asyncio.sleep(0.1)
            yield "!"

        exclamation_chain = Chain[str, str]("ExclamationChain", exclamation_output)

        async def upper_pipe(stream):
            async for value in stream:
                yield value.upper()

        chain: Chain[str, str] = exclamation_chain.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(chain("Hello World"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", data="Hello World", final=False),
                ChainOutput(
                    chain="ExclamationChain@map", data="hello world", final=False
                ),
                ChainOutput(
                    chain="ExclamationChain@map@pipe", data="HELLO WORLD", final=True
                ),
                ChainOutput(chain="ExclamationChain", data="!", final=False),
                ChainOutput(chain="ExclamationChain@map", data="!", final=False),
                ChainOutput(chain="ExclamationChain@map@pipe", data="!", final=True),
            ],
        )

    async def test_it_keep_piping_previous_values_even_if_there_is_a_delay_in_pipe(
        self,
    ):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )

        async def upper_pipe(stream):
            async for value in stream:
                await asyncio.sleep(0.1)
                yield value.upper()

        chain: Chain[str, str] = exclamation_chain.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(chain("Hello World"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", data="Hello World", final=False),
                ChainOutput(
                    chain="ExclamationChain@map", data="hello world", final=False
                ),
                ChainOutput(chain="ExclamationChain", data="!", final=False),
                ChainOutput(chain="ExclamationChain@map", data="!", final=False),
                ChainOutput(
                    chain="ExclamationChain@map@pipe", data="HELLO WORLD", final=True
                ),
                ChainOutput(chain="ExclamationChain@map@pipe", data="!", final=True),
            ],
        )

    async def test_it_can_pipe_another_chain(self):
        exclamation_chain = Chain[str, str](
            "ExclamationChain", lambda input: as_async_generator(f"{input}", "!")
        )
        uppercase_chain = Chain[str, str]("UppercaseChain", lambda input: input.upper())

        async def upper_pipe(stream):
            async for value in stream:
                async for output in uppercase_chain(value):
                    yield output

        chain: Chain[str, str] = exclamation_chain.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(chain("Hello World"))
        self.assertEqual(
            result,
            [
                ChainOutput(chain="ExclamationChain", data="Hello World", final=False),
                ChainOutput(
                    chain="ExclamationChain@map", data="hello world", final=False
                ),
                ChainOutput(chain="UppercaseChain", data="HELLO WORLD", final=True),
                ChainOutput(chain="ExclamationChain", data="!", final=False),
                ChainOutput(chain="UppercaseChain", data="!", final=True),
                ChainOutput(chain="ExclamationChain@map", data="!", final=False),
            ],
        )

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
            ChainOutput(chain="ExclamationChain", data="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", data="!", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain", data="hello world, !", final=True),
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
            ChainOutput(chain="HelloChain", data="hello ", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="HelloChain", data="world", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="BlockingChain@join", data="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", data="hello world!", final=True),
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
                ChainOutput(chain="RangeChain", data=i, final=False),
            )
            self.assertEqual(
                await next_item(outputs),
                ChainOutput(chain="RangeChain@map", data=i + 1, final=False),
            )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="RangeChain@map@collect", data=[1, 2, 3, 4, 5], final=True
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
                ChainOutput(chain="ParallelChain", data=i, final=False),
            )
            self.assertIsInstance(
                (await next_item(outputs)).data,
                AsyncGenerator,
            )
        collect_next = await next_item(outputs)
        self.assertEqual(len(cast(List, collect_next.data)), 100)
        self.assertIsInstance(
            cast(List, collect_next.data)[0],
            AsyncGenerator,
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather",
                data=[[i + 1] for i in range(0, 100)],
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather@and_then",
                data=5050,
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ParallelChain@map@collect@gather@and_then@map",
                data="5050",
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

    async def test_it_handles_errors(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        chain = Chain[str, str](
            "GreetingChain",
            raising_function,
        ).on_error(
            lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
        )

        outputs = chain("418")

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                ChainOutput(
                    chain="GreetingChain",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot",
                final=True,
            ),
        )

    async def test_it_handles_errors_only_if_they_happen_before_the_specified_handler(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        chain = (
            Chain[str, str](
                "GreetingChain",
                lambda input: f"Hello {input}, how are you doing?",
            )
            .on_error(
                lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
            )
            .and_then(lambda input: [raising_function(item) for item in input])
        )

        outputs = chain("Dave")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain",
                data="Hello Dave, how are you doing?",
                final=False,
            ),
        )

        with self.assertRaises(Exception) as raised:
            await next_item(outputs)

        self.assertIn("I'm a teapot", str(raised.exception))

    async def test_it_handles_errors_happening_mid_stream(
        self,
    ):
        async def raising_function(input: str):
            yield "hi"
            yield "there"
            raise Exception(f"{input} I'm a teapot")

        chain = Chain[str, str](
            "GreetingChain",
            raising_function,
        ).on_error(
            lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
        )

        outputs = chain("418")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain",
                data="hi",
                final=True,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain",
                data="there",
                final=True,
            ),
        )

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                ChainOutput(
                    chain="GreetingChain",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot",
                final=True,
            ),
        )

    async def test_it_accepts_a_different_type_coming_from_the_error_handling(
        self,
    ):
        def raising_function(input: str):
            if input == "418":
                raise Exception(f"{input} I'm a teapot")
            else:
                return "all good?"

        chain = (
            Chain[str, str](
                "GreetingChain",
                raising_function,
            )
            .on_error(lambda err: 500)
            .and_then(
                lambda tokens: "".join(
                    [
                        f"an int {token}"
                        if isinstance(token, int)
                        else f"a str {token}"
                        for token in tokens
                    ]
                )
            )
        )

        outputs = chain("200")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain",
                data="all good?",
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error@and_then",
                data="a str all good?",
                final=True,
            ),
        )

        outputs = chain("418")

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                ChainOutput(
                    chain="GreetingChain",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error",
                data=500,
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error@and_then",
                data="an int 500",
                final=True,
            ),
        )


class SingleOutputChainTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_chain = SingleOutputChain[str, str](
            "ExclamationChain", lambda input: f"{input}!"
        )

        outputs = exclamation_chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", data="hello world!", final=True),
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

    async def test_it_is_mappable(self):
        exclamation_chain = SingleOutputChain[str, str](
            "ExclamationChain", lambda input: f"{input}!"
        )
        chain = exclamation_chain.map(lambda input: input.replace("world", "planet"))

        outputs = chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain", data="hello world!", final=False),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="ExclamationChain@map", data="hello planet!", final=True),
        )

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
                chain="ExclamationListChain", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain", data="hello world, !", final=False),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(chain="JoinerChain@map", data="hello world, !~", final=True),
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
                chain="ExclamationListChain", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@and_then",
                data="hello world, !",
                final=True,
            ),
        )

    async def test_it_is_thenable_with_async_generator_return(self):
        exclamation_list_chain = SingleOutputChain[str, List[str]](
            "ExclamationListChain", lambda input: [f"{input}", "!"]
        )

        chain: Chain[str, str] = exclamation_list_chain.and_then(
            lambda input: as_async_generator(*(s + ", " for s in input))
        )

        outputs = chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@and_then",
                data="hello world, ",
                final=True,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@and_then",
                data="!, ",
                final=True,
            ),
        )

    async def test_it_is_pipeable_working_like_and_then(self):
        exclamation_list_chain = SingleOutputChain[str, List[str]](
            "ExclamationListChain", lambda input: [f"{input}", "!"]
        )

        async def comma_pipe(stream):
            async for input in stream:
                for s in input:
                    yield s + ", "

        chain: Chain[str, str] = exclamation_list_chain.pipe(comma_pipe)

        outputs = chain("hello world")
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@pipe",
                data="hello world, ",
                final=True,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="ExclamationListChain@pipe",
                data="!, ",
                final=True,
            ),
        )

    async def test_it_handles_errors(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        chain = (
            SingleOutputChain[str, str](
                "GreetingChain",
                raising_function,
            )
            .on_error(
                lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
            )
            .and_then(lambda greeting: greeting + " :)")
        )

        outputs = chain("418")

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot",
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            ChainOutput(
                chain="GreetingChain@on_error@and_then",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot :)",
                final=True,
            ),
        )
