import unittest
import asyncio
import random
import unittest
from typing import (
    Any,
    AsyncGenerator,
    Iterable,
    List,
    Optional,
    TypeVar,
    TypedDict,
    cast,
)

from langstream.core.stream import Stream, StreamOutput, SingleOutputStream
from langstream.utils.async_generator import as_async_generator, collect, next_item
from langstream.utils.stream import join_final_output, collect_final_output

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


class StreamTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: f"{input}!"
        )

        result = await collect(exclamation_stream("hello world"))
        self.assertEqual(
            result,
            [StreamOutput(stream="ExclamationStream", data="hello world!", final=True)],
        )

    async def test_it_is_callable_with_async_iterable_return(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(input, "!")
        )

        result = await collect(exclamation_stream("hello world"))
        self.assertEqual(
            result,
            [
                StreamOutput(stream="ExclamationStream", data="hello world", final=True),
                StreamOutput(stream="ExclamationStream", data="!", final=True),
            ],
        )

    async def test_it_is_mappable_as_values_arrive(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(input, "!")
        )
        stream = exclamation_stream.map(
            lambda input: input.replace("world", "planet")
        ).map(lambda input: input + "~")

        result = await collect(stream("hello world"))
        self.assertEqual(
            result,
            [
                StreamOutput(
                    stream="ExclamationStream",
                    data="hello world",
                    final=False,
                ),
                StreamOutput(
                    stream="ExclamationStream@map",
                    data="hello planet",
                    final=False,
                ),
                StreamOutput(
                    stream="ExclamationStream@map@map",
                    data="hello planet~",
                    final=True,
                ),
                StreamOutput(
                    stream="ExclamationStream",
                    data="!",
                    final=False,
                ),
                StreamOutput(
                    stream="ExclamationStream@map",
                    data="!",
                    final=False,
                ),
                StreamOutput(
                    stream="ExclamationStream@map@map",
                    data="!~",
                    final=True,
                ),
            ],
        )

        result = await join_final_output(stream("hello world"))
        self.assertEqual(result, "hello planet~!~")

    async def test_it_is_filterable(self):
        numbers_stream = Stream[int, int](
            "NumbersStream", lambda input: as_async_generator(*range(0, input))
        )
        stream = numbers_stream.filter(lambda input: input % 2 == 0)

        result = await collect(stream(4))
        self.assertEqual(
            result,
            [
                StreamOutput(
                    stream="NumbersStream",
                    data=0,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@filter",
                    data=0,
                    final=True,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=1,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=2,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@filter",
                    data=2,
                    final=True,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=3,
                    final=False,
                ),
            ],
        )

    async def test_it_is_thenable(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )
        stream = exclamation_stream.and_then(lambda input: ", ".join(input))

        result = await collect(stream("hello world"))
        self.assertEqual(
            result[-1],
            StreamOutput(
                stream="ExclamationStream@and_then",
                data="hello world, !",
                final=True,
            ),
        )

    async def test_it_is_thenable_with_single_value_return(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )

        stream = exclamation_stream.and_then(lambda input: ", ".join(input))

        result = await join_final_output(stream("hello world"))
        self.assertEqual(result, "hello world, !")

    async def test_it_is_pipeable(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )

        async def upper_pipe(stream):
            async for value in stream:
                yield value.upper()

        stream: Stream[str, str] = exclamation_stream.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(stream("Hello World"))
        self.assertEqual(
            result,
            [
                StreamOutput(stream="ExclamationStream", data="Hello World", final=False),
                StreamOutput(
                    stream="ExclamationStream@map", data="hello world", final=False
                ),
                StreamOutput(
                    stream="ExclamationStream@map@pipe", data="HELLO WORLD", final=True
                ),
                StreamOutput(stream="ExclamationStream", data="!", final=False),
                StreamOutput(stream="ExclamationStream@map@pipe", data="!", final=True),
                StreamOutput(stream="ExclamationStream@map", data="!", final=False),
            ],
        )

    async def test_it_is_pipeable_with_a_delay_on_producer(self):
        async def exclamation_output(input) -> AsyncGenerator[str, Any]:
            yield input
            await asyncio.sleep(0.1)
            yield "!"

        exclamation_stream = Stream[str, str]("ExclamationStream", exclamation_output)

        async def upper_pipe(stream):
            async for value in stream:
                yield value.upper()

        stream: Stream[str, str] = exclamation_stream.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(stream("Hello World"))
        self.assertEqual(
            result,
            [
                StreamOutput(stream="ExclamationStream", data="Hello World", final=False),
                StreamOutput(
                    stream="ExclamationStream@map", data="hello world", final=False
                ),
                StreamOutput(
                    stream="ExclamationStream@map@pipe", data="HELLO WORLD", final=True
                ),
                StreamOutput(stream="ExclamationStream", data="!", final=False),
                StreamOutput(stream="ExclamationStream@map", data="!", final=False),
                StreamOutput(stream="ExclamationStream@map@pipe", data="!", final=True),
            ],
        )

    async def test_it_keep_piping_previous_values_even_if_there_is_a_delay_in_pipe(
        self,
    ):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )

        async def upper_pipe(stream):
            async for value in stream:
                await asyncio.sleep(0.1)
                yield value.upper()

        stream: Stream[str, str] = exclamation_stream.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(stream("Hello World"))
        self.assertEqual(
            result,
            [
                StreamOutput(stream="ExclamationStream", data="Hello World", final=False),
                StreamOutput(
                    stream="ExclamationStream@map", data="hello world", final=False
                ),
                StreamOutput(stream="ExclamationStream", data="!", final=False),
                StreamOutput(stream="ExclamationStream@map", data="!", final=False),
                StreamOutput(
                    stream="ExclamationStream@map@pipe", data="HELLO WORLD", final=True
                ),
                StreamOutput(stream="ExclamationStream@map@pipe", data="!", final=True),
            ],
        )

    async def test_it_can_pipe_another_stream(self):
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )
        uppercase_stream = Stream[str, str]("UppercaseStream", lambda input: input.upper())

        async def upper_pipe(stream):
            async for value in stream:
                async for output in uppercase_stream(value):
                    yield output

        stream: Stream[str, str] = exclamation_stream.map(lambda x: x.lower()).pipe(
            upper_pipe
        )

        result = await collect(stream("Hello World"))
        self.assertEqual(
            result,
            [
                StreamOutput(stream="ExclamationStream", data="Hello World", final=False),
                StreamOutput(
                    stream="ExclamationStream@map", data="hello world", final=False
                ),
                StreamOutput(stream="UppercaseStream", data="HELLO WORLD", final=True),
                StreamOutput(stream="ExclamationStream", data="!", final=False),
                StreamOutput(stream="UppercaseStream", data="!", final=True),
                StreamOutput(stream="ExclamationStream@map", data="!", final=False),
            ],
        )

    async def test_it_gets_the_results_as_they_come(self):
        blocked = True

        async def block_for_flag(xs: Iterable[T]) -> AsyncGenerator[T, Any]:
            while blocked:
                pass
            for x in xs:
                yield x

        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: as_async_generator(f"{input}", "!")
        )
        blocking_stream = Stream[Iterable[str], str]("BlockingStream", block_for_flag)
        JoinerStream = Stream[Iterable[str], str](
            "JoinerStream", lambda input: ", ".join(input)
        )

        stream = exclamation_stream.and_then(blocking_stream).and_then(JoinerStream)

        outputs = stream("hello world")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream", data="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream", data="!", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="JoinerStream", data="hello world, !", final=True),
        )

    async def test_it_is_composable_by_waiting_the_first_stream_to_finish(self):
        blocked = True

        async def block_for_flag(xs: Iterable[T]) -> AsyncGenerator[T, Any]:
            while blocked:
                pass
            for x in xs:
                yield x

        hello_stream = Stream[str, str](
            "HelloStream", lambda input: as_async_generator("hello ", input)
        )
        blocking_stream = Stream[Iterable[str], str]("BlockingStream", block_for_flag)
        exclamation_stream = Stream[str, str](
            "ExclamationStream", lambda input: f"{input}!"
        )

        stream = hello_stream.and_then(blocking_stream).join().and_then(exclamation_stream)

        outputs = stream("world")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="HelloStream", data="hello ", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="HelloStream", data="world", final=False),
        )

        blocked = False
        await next_item(outputs)
        await next_item(outputs)

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="BlockingStream@join", data="hello world", final=False),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream", data="hello world!", final=True),
        )

    async def test_it_collects_the_outputs_to_a_list(self):
        stream: Stream[int, List[int]] = (
            Stream[int, int](
                "RangeStream", lambda start: as_async_generator(*range(start, 5))
            )
            .map(lambda input: input + 1)
            .collect()
        )

        outputs = stream(0)
        for i in range(0, 5):
            self.assertEqual(
                await next_item(outputs),
                StreamOutput(stream="RangeStream", data=i, final=False),
            )
            self.assertEqual(
                await next_item(outputs),
                StreamOutput(stream="RangeStream@map", data=i + 1, final=False),
            )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="RangeStream@map@collect", data=[1, 2, 3, 4, 5], final=True
            ),
        )

    async def test_it_can_process_many_things_in_parallel(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        stream: Stream[int, str] = (
            Stream[int, int](
                "ParallelStream", lambda start: as_async_generator(*range(start, 100))
            )
            .map(increment_number)
            .collect()
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        outputs = stream(0)

        for i in range(0, 100):
            self.assertEqual(
                await next_item(outputs),
                StreamOutput(stream="ParallelStream", data=i, final=False),
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
            StreamOutput(
                stream="ParallelStream@map@collect@gather",
                data=[[i + 1] for i in range(0, 100)],
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ParallelStream@map@collect@gather@and_then",
                data=5050,
                final=False,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ParallelStream@map@collect@gather@and_then@map",
                data="5050",
                final=True,
            ),
        )

    async def test_it_can_gather_stream_mappings(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        inc_stream = SingleOutputStream[int, int]("IncStream", increment_number)

        stream: Stream[int, str] = (
            Stream[int, int](
                "ParallelStream", lambda start: as_async_generator(*range(start, 100))
            )
            .map(inc_stream)
            .collect()
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        result = await join_final_output(stream(0))
        self.assertEqual(result, "5050")

    async def test_it_can_gather_direclty_from_the_stream(self):
        async def increment_number(num: int) -> AsyncGenerator[int, Any]:
            await asyncio.sleep(random.random() * 0.5)  # heavy processing
            yield num + 1

        stream: Stream[int, str] = (
            Stream[int, int](
                "ParallelStream", lambda start: as_async_generator(*range(start, 100))
            )
            .map(increment_number)
            .gather()
            .and_then(lambda result: sum([x[0] for x in result]))
            .map(lambda x: str(x))
        )

        result = await join_final_output(stream(0))
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

        stream = Stream[str, str](
            "GreetingStream",
            lambda input: "how are you?"
            if "hello" in memory["history"]
            else f"hello {input}",
        ).map(save_to_memory)

        result = await join_final_output(stream("José"))
        self.assertEqual(result, "hello José")

        result = await join_final_output(stream("hello"))
        self.assertEqual(result, "how are you?")

    async def test_it_handles_errors(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        stream = Stream[str, str](
            "GreetingStream",
            raising_function,
        ).on_error(
            lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
        )

        outputs = stream("418")

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                StreamOutput(
                    stream="GreetingStream",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot",
                final=True,
            ),
        )

    async def test_it_handles_errors_only_if_they_happen_before_the_specified_handler(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        stream = (
            Stream[str, str](
                "GreetingStream",
                lambda input: f"Hello {input}, how are you doing?",
            )
            .on_error(
                lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
            )
            .and_then(lambda input: [raising_function(item) for item in input])
        )

        outputs = stream("Dave")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream",
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

        stream = Stream[str, str](
            "GreetingStream",
            raising_function,
        ).on_error(
            lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
        )

        outputs = stream("418")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream",
                data="hi",
                final=True,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream",
                data="there",
                final=True,
            ),
        )

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                StreamOutput(
                    stream="GreetingStream",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error",
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

        stream = (
            Stream[str, str](
                "GreetingStream",
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

        outputs = stream("200")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream",
                data="all good?",
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error@and_then",
                data="a str all good?",
                final=True,
            ),
        )

        outputs = stream("418")

        self.assertEqual(
            str(await next_item(outputs)),
            str(
                StreamOutput(
                    stream="GreetingStream",
                    data=Exception(f"418 I'm a teapot"),
                    final=False,
                )
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error",
                data=500,
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error@and_then",
                data="an int 500",
                final=True,
            ),
        )


class SingleOutputStreamTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_it_is_callable_with_single_value_return(self):
        exclamation_stream = SingleOutputStream[str, str](
            "ExclamationStream", lambda input: f"{input}!"
        )

        outputs = exclamation_stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream", data="hello world!", final=True),
        )

    @unittest.skip("TODO")
    async def test_it_is_callable_with_async_return(self):
        async def async_exclamation(input: str):
            return f"{input}!"

        exclamation_stream = SingleOutputStream[str, str](
            "ExclamationStream", lambda input: async_exclamation(input)  # type: ignore (TODO)
        )

        result = await join_final_output(exclamation_stream("hello world"))
        self.assertEqual(result, "hello world!")

    async def test_it_is_mappable(self):
        exclamation_stream = SingleOutputStream[str, str](
            "ExclamationStream", lambda input: f"{input}!"
        )
        stream = exclamation_stream.map(lambda input: input.replace("world", "planet"))

        outputs = stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream", data="hello world!", final=False),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="ExclamationStream@map", data="hello planet!", final=True),
        )

    async def test_it_is_filterable_by_returning_none_when_filtered_out(self):
        stream: Stream[int, Optional[List[int]]] = (
            Stream[int, int](
                "NumbersStream", lambda input: as_async_generator(*range(0, input))
            )
            .collect()
            .filter(lambda numbers: all([n % 2 == 0 for n in numbers]))
        )

        result = await collect(stream(4))
        self.assertEqual(
            result,
            [
                StreamOutput(
                    stream="NumbersStream",
                    data=0,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=1,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=2,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream",
                    data=3,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@collect",
                    data=[0, 1, 2, 3],
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@collect@filter",
                    data=None,
                    final=True,
                ),
            ],
        )

        result = await collect(stream(1))
        self.assertEqual(
            result,
            [
                StreamOutput(
                    stream="NumbersStream",
                    data=0,
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@collect",
                    data=[0],
                    final=False,
                ),
                StreamOutput(
                    stream="NumbersStream@collect@filter",
                    data=[0],
                    final=True,
                ),
            ],
        )

    async def test_it_is_thenable_keeping_the_proper_stream_names(self):
        exclamation_list_stream = SingleOutputStream[str, List[str]](
            "ExclamationListStream", lambda input: [f"{input}", "!"]
        )
        joiner_stream = Stream[Iterable[str], str](
            "JoinerStream", lambda input: ", ".join(input)
        )

        stream = exclamation_list_stream.and_then(joiner_stream).map(
            lambda input: input + "~"
        )

        outputs = stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="JoinerStream", data="hello world, !", final=False),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(stream="JoinerStream@map", data="hello world, !~", final=True),
        )

    async def test_it_is_thenable_with_single_value_return(self):
        exclamation_list_stream = SingleOutputStream[str, List[str]](
            "ExclamationListStream", lambda input: [f"{input}", "!"]
        )

        stream = exclamation_list_stream.and_then(lambda input: ", ".join(input))

        outputs = stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream@and_then",
                data="hello world, !",
                final=True,
            ),
        )

    async def test_it_is_thenable_with_async_generator_return(self):
        exclamation_list_stream = SingleOutputStream[str, List[str]](
            "ExclamationListStream", lambda input: [f"{input}", "!"]
        )

        stream: Stream[str, str] = exclamation_list_stream.and_then(
            lambda input: as_async_generator(*(s + ", " for s in input))
        )

        outputs = stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream@and_then",
                data="hello world, ",
                final=True,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream@and_then",
                data="!, ",
                final=True,
            ),
        )

    async def test_it_is_pipeable_working_like_and_then(self):
        exclamation_list_stream = SingleOutputStream[str, List[str]](
            "ExclamationListStream", lambda input: [f"{input}", "!"]
        )

        async def comma_pipe(stream):
            async for input in stream:
                for s in input:
                    yield s + ", "

        stream: Stream[str, str] = exclamation_list_stream.pipe(comma_pipe)

        outputs = stream("hello world")
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream", data=["hello world", "!"], final=False
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream@pipe",
                data="hello world, ",
                final=True,
            ),
        )
        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="ExclamationListStream@pipe",
                data="!, ",
                final=True,
            ),
        )

    async def test_it_handles_errors(
        self,
    ):
        def raising_function(input: str):
            raise Exception(f"{input} I'm a teapot")

        stream = (
            SingleOutputStream[str, str](
                "GreetingStream",
                raising_function,
            )
            .on_error(
                lambda err: f"I'm Sorry Dave, I'm Afraid I Can't Do That: {str(err)}"
            )
            .and_then(lambda greeting: greeting + " :)")
        )

        outputs = stream("418")

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot",
                final=False,
            ),
        )

        self.assertEqual(
            await next_item(outputs),
            StreamOutput(
                stream="GreetingStream@on_error@and_then",
                data="I'm Sorry Dave, I'm Afraid I Can't Do That: 418 I'm a teapot :)",
                final=True,
            ),
        )

    async def test_it_is_redundantly_collectable(self):
        stream: Stream[int, List[List[int]]] = (
            Stream[int, int](
                "NumbersStream", lambda input: as_async_generator(*range(0, input))
            )
            .collect()
            .collect()
        )

        result = await collect_final_output(stream(4))
        self.assertEqual(
            result,
            [[0, 1, 2, 3]],
        )
