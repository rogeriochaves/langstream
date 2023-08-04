"""
Core Stream module
"""
import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import asyncstdlib

from langstream.utils.async_generator import as_async_generator, merge
from langstream.utils._typing import unwrap

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
X = TypeVar("X")


@dataclass
class StreamOutput(Generic[T]):
    """
    StreamOutput is a data class that represents the output of a Stream at each step.

    Attributes
    ----------
    stream : str
        The name of the stream that produced this output. This helps in identifying
        which part of the processing pipeline the output is coming from.

    output : Union[T, Any]
        The actual output data produced by the stream. This will be type T for final stream output,
        but can be also be of any type produced by any step of the whole stream.

    final : bool
        A boolean flag indicating whether this output is the final output of the stream.
        Only the outputs at the end of the stream are marked as "final".

    Example
    -------

    >>> from langstream import Stream
    >>> import asyncio
    ...
    >>> async def example():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
    ...     polite_stream = greet_stream.map(lambda greeting: f"{greeting} How are you?")
    ...
    ...     async for output in polite_stream("Alice"):
    ...         # Output is of type StreamOutput
    ...         print(output)
    ...
    >>> asyncio.run(example())
    StreamOutput(stream='GreetingStream', data='Hello, Alice!', final=False)
    StreamOutput(stream='GreetingStream@map', data='Hello, Alice! How are you?', final=True)
    """

    stream: str
    data: Union[T, Any]
    final: bool


class Stream(Generic[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[StreamOutput[U], Any], AsyncGenerator[U, Any], U]
    ]

    def __init__(
        self,
        name: str,
        call: Callable[
            [T],
            Union[AsyncGenerator[StreamOutput[U], Any], AsyncGenerator[U, Any], U],
        ],
    ) -> None:
        self.name = name
        self._call = call

    def __call__(self, input: T) -> AsyncGenerator[StreamOutput[U], Any]:
        result = self._call(input)
        return self._wrap(result)

    def _wrap(
        self,
        value: Union[AsyncGenerator[StreamOutput[V], Any], AsyncGenerator[V, Any], V],
        final: Optional[bool] = None,
        name: Optional[str] = None,
    ) -> AsyncGenerator[StreamOutput[V], Any]:
        async def _wrap(
            values: Union[AsyncGenerator[StreamOutput[V], Any], AsyncGenerator[V, Any]],
        ) -> AsyncGenerator[StreamOutput[V], Any]:
            async for value in values:
                yield self._output_wrap(value, final=final, name=name)

        if isinstance(value, AsyncGenerator):
            return _wrap(value)
        return _wrap(as_async_generator(value))

    def _output_wrap(
        self, value: Union[StreamOutput[V], V], final=None, name=None
    ) -> StreamOutput[V]:
        if isinstance(value, StreamOutput):
            final = final if final is not None else value.final
            return StreamOutput[V](stream=value.stream, data=value.data, final=final)

        final = final if final is not None else True
        return StreamOutput[V](
            stream=self.name if name is None else name, data=value, final=final
        )

    async def _reyield(
        self, async_iterable: AsyncGenerator[StreamOutput[U], Any]
    ) -> AsyncGenerator[Tuple[List[U], StreamOutput[U]], Any]:
        values: List[U] = []
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                values.append(u.data)
            yield (values, u_rewrapped)

    def map(self, fn: Callable[[U], V]) -> "Stream[T, V]":
        """
        Maps the output of the current stream through a function as they arrive.

        The transform function will receive the current output of the stream and
        should return a modified version of it. This method is non-blocking and
        will continue processing the stream in parallel.

        Example:

        >>> from langstream import Stream, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
        ...     polite_stream = greet_stream.map(lambda greeting: f"{greeting} How are you?")
        ...     return await join_final_output(polite_stream("Alice"))
        ...
        >>> asyncio.run(example())
        'Hello, Alice! How are you?'


        Example of processing one token at a time:

        >>> from langstream import Stream, as_async_generator, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_stream = Stream[str, str]("WordsStream", lambda sentence: as_async_generator(*sentence.split(" "))) # produces one word at a time
        ...     accronym_stream = words_stream.map(lambda word: word.upper()[0]) # uppercases each word and take the first letter
        ...     return await join_final_output(accronym_stream("as soon as possible"))
        ...
        >>> asyncio.run(example())
        'ASAP'
        """

        next_name = f"{self.name}@map"

        async def map(input: T) -> AsyncGenerator[StreamOutput[V], Any]:
            # Reyield previous stream so we never block the stream, and at the same time yield mapped values
            prev_len_values = 0
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[V], to_reyield)
                if len(values) > prev_len_values:  # as soon as there is a new value
                    prev_len_values = len(values)
                    yield self._output_wrap(fn(values[-1]), name=next_name)

        return Stream[T, V](next_name, lambda input: map(input))

    def filter(self, fn: Callable[[U], bool]) -> "Stream[T, U]":
        """
        Filters the output of the current stream, keeping only the values that return True.

        This method is non-blocking and expects a function that returns True for keeping the value,
        or False for dropping it, as they arrive.

        Example:

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     numbers_stream = Stream[int, int]("NumbersStream", lambda input: as_async_generator(*range(0, input)))
        ...     even_stream = numbers_stream.filter(lambda input: input % 2 == 0)
        ...     return await collect_final_output(even_stream(9))
        ...
        >>> asyncio.run(example())
        [0, 2, 4, 6, 8]
        """

        next_name = f"{self.name}@filter"

        async def filter(input: T) -> AsyncGenerator[StreamOutput[U], Any]:
            # Reyield previous stream so we never block the stream, and at the same time yield mapped values
            prev_len_values = 0
            async for values, to_reyield in self._reyield(self(input)):
                yield to_reyield
                if len(values) > prev_len_values:  # as soon as there is a new value
                    prev_len_values = len(values)
                    if fn(values[-1]):
                        yield self._output_wrap(values[-1], name=next_name)

        return Stream[T, U](next_name, lambda input: filter(input))

    def and_then(
        self,
        next: Callable[
            [Iterable[U]],
            Union[AsyncGenerator[StreamOutput[V], Any], AsyncGenerator[V, Any], V],
        ],
    ) -> "Stream[T, V]":
        """
        Processes the output of the current stream through a transformation function or another stream.

        Unlike the map method, which applies transformations to outputs as they arrive,
        the and_then method first collects all the outputs and then passes them to the transformation function or the next stream.
        This method is blocking and will wait for the entire stream to be processed before applying the transformation.

        If `transform` is a function, it should accept the list of collected outputs and return a modified version of it.
        If `transform` is another stream, it is used to process the list of collected outputs.

        Example using a function:

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     word_stream = Stream[str, str]("WordStream", lambda word: as_async_generator(word, "!"))
        ...     count_stream : Stream[str, int] = word_stream.and_then(lambda outputs: len(list(outputs)))
        ...     return await collect_final_output(count_stream("Hi"))
        ...
        >>> asyncio.run(example())
        [2]


        Example using another stream:

        >>> from langstream import Stream, as_async_generator, join_final_output
        >>> from typing import Iterable
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_stream = Stream[str, str]("WordsStream", lambda sentence: as_async_generator(*sentence.split(" "))) # produces one word at a time
        ...     acronym_stream = Stream[Iterable[str], str]("AcronymStream", lambda words: "".join(word.upper()[0] for word in words)) # produces acronym
        ...     composed_stream = words_stream.and_then(acronym_stream)
        ...     return await join_final_output(composed_stream("as soon as possible"))
        ...
        >>> asyncio.run(example())
        'ASAP'
        """

        next_name = f"{self.name}@and_then"
        if hasattr(next, "name"):
            next_name = next.name

        async def and_then(
            input: T,
        ) -> AsyncGenerator[StreamOutput[V], Any]:
            # First, reyield previous stream so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[V], to_reyield)
                iter_u = values

            # Then, call in the next stream
            iter_v = self._wrap(next(iter_u), name=next_name)
            async for v in iter_v:
                yield v

        return Stream[T, V](next_name, and_then)

    def pipe(
        self,
        fn: Callable[
            [AsyncGenerator[U, Any]], AsyncGenerator[Union[StreamOutput[V], V], Any]
        ],
    ) -> "Stream[T, V]":
        """
        Lower level constructor to pipe a stream into another one, giving you the underlying AsyncGenerator.
        Pipe takes a callback function which should always produce an AsyncGenerator in return, which means you
        need to declare an async function and your function needs to use `yield` for generating values, the advantage
        of that is that you have fine control on whether it will be blocking the stream or not.

        In fact, with pipe you can reconstruct `map` and `and_then`, for example:

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> from typing import List, AsyncGenerator
        >>> import asyncio
        ...
        >>> async def example(items):
        ...     async def mario_pipe(stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        ...        waiting_for_mushroom = False
        ...        async for item in stream:
        ...            if item == "Mario":
        ...                waiting_for_mushroom = True
        ...            elif item == "Mushroom" and waiting_for_mushroom:
        ...                yield "Super Mario!"
        ...            else:
        ...                yield item + "?"
        ...
        ...     piped_stream = Stream[List[str], str](
        ...         "PipedStream", lambda items: as_async_generator(*items)
        ...     ).pipe(mario_pipe)
        ...
        ...     return await collect_final_output(piped_stream(items))
        ...
        >>> asyncio.run(example(["Mario", "Mushroom"]))
        ['Super Mario!']
        >>> asyncio.run(example(["Luigi"]))
        ['Luigi?']
        >>> asyncio.run(example(["Mario", "Luigi", "Mushroom"]))
        ['Luigi?', 'Super Mario!']

        As you can see this pipe blocks kinda like `and_then` when it sees "Mario", until a mushroom arrives, but for other random items
        such as "Luigi" it just re-yields it immediately, adding a question mark, non-blocking, like `map`.

        You can also call another stream from `pipe` directly, just be sure to re-yield its outputs
        """

        next_name = f"{self.name}@pipe"

        async def filter_final_output(
            async_iterable: AsyncGenerator[StreamOutput[U], Any]
        ) -> AsyncGenerator[U, Any]:
            async for output in async_iterable:
                if output.final:
                    yield cast(U, output.data)

        def pipe(input: T) -> AsyncGenerator[StreamOutput[V], Any]:
            previous, final = asyncstdlib.tee(self(input), n=2, lock=asyncio.Lock())

            previous = self._wrap(previous, name=next_name, final=False)
            previous = cast(AsyncGenerator[StreamOutput[V], Any], previous)

            final = filter_final_output(
                cast(AsyncGenerator[StreamOutput[U], Any], final)
            )
            final = cast(
                AsyncGenerator[StreamOutput[V], Any],
                self._wrap(fn(final), name=next_name),
            )

            return merge(previous, final)

        return Stream[T, V](next_name, pipe)

    def collect(self: "Stream[T, U]") -> "SingleOutputStream[T, List[U]]":
        """
        Collects all the outputs produced by the stream and returns them as a list.

        This method is blocking useful when the next stream or processing step needs to have access to the
        entire output all at once, rather than processing elements as they arrive.

        Example:

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     word_stream: Stream[str, List[str]] = Stream[str, str](
        ...         "WordStream", lambda word: as_async_generator(word, "!")
        ...     ).collect()
        ...     return await collect_final_output(word_stream("Hi"))
        ...
        >>> asyncio.run(example())
        [['Hi', '!']]
        """

        next_name = f"{self.name}@collect"

        async def _collect(
            input: T,
        ) -> AsyncGenerator[StreamOutput[List[U]], Any]:
            # First, reyield previous stream so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[List[U]], to_reyield)
                iter_u = values

            # Then, yield the collected results
            yield self._output_wrap(iter_u, name=next_name)

        return SingleOutputStream[T, List[U]](next_name, _collect)

    def join(self: "Stream[T, str]", separator="") -> "SingleOutputStream[T, str]":
        """
        Joins the output of a string-producing stream into a single string.

        The `join` method concatenates each item in the output of the stream, using the
        provided separator between each element. This is particularly useful when working
        with text, and you want to merge all the generated tokens.

        Note that this method blocks until all outputs of the stream are available, as it
        needs to wait for the complete output to perform the join operation.

        Params
        ----------
        separator : str
            A string that will be used as a separator between the elements. Default is an empty string.

        Example:

        >>> from langstream import Stream, as_async_generator, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_stream = Stream[str, str]("WordsStream", lambda sentence: as_async_generator(*sentence.split(" ")))
        ...     capitalized_stream = words_stream.map(lambda word: word.capitalize())
        ...     joined_stream = capitalized_stream.join(" ")
        ...     return await join_final_output(joined_stream("this is an example"))
        ...
        >>> asyncio.run(example())
        'This Is An Example'
        """

        next_name = f"{self.name}@join"

        async def _join(
            input: T,
        ) -> AsyncGenerator[StreamOutput[str], Any]:
            # First, reyield previous stream so we never block the stream, and collect the results until they are done
            iter_u: Iterable[str] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield to_reyield
                iter_u = values

            # Then, return the joined result
            output: str = separator.join(iter_u)
            yield self._output_wrap(output, name=next_name)

        return SingleOutputStream[T, str](next_name, _join)

    def gather(
        self: "Union[Stream[T, AsyncGenerator[StreamOutput[V], Any]], Stream[T, AsyncGenerator[V, Any]]]",
    ) -> "SingleOutputStream[T, List[List[V]]]":
        """
        Gathers results from multiple streams and processes them in parallel.

        The `gather` method is used to process several streams concurrently, and it waits until all of
        them are complete before continuing. This is similar to `asyncio.gather`, and is useful when you
        want to run multiple asynchronous tasks in parallel and wait for all of them to complete.

        Note that the order of results corresponds to the order of streams passed to the `gather` method.

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def delayed_output(x):
        ...     await asyncio.sleep(0.1)
        ...     yield f"Number: {x}"
        ...
        >>> async def example():
        ...     number_stream = Stream[int, int](
        ...         "NumberStream", lambda x: as_async_generator(*range(x))
        ...     )
        ...     gathered_stream : Stream[int, str] = (
        ...         number_stream.map(delayed_output)
        ...         .gather()
        ...         .and_then(lambda results: as_async_generator(*(r[0] for r in results)))
        ...     )
        ...     return await collect_final_output(gathered_stream(3))
        ...
        >>> asyncio.run(example()) # will take 0.1s to finish, not 0.3s, because it runs in parallel
        ['Number: 0', 'Number: 1', 'Number: 2']
        """
        return self.collect().gather()

    def on_error(
        self,
        handler: Callable[[Exception], Union[AsyncGenerator[StreamOutput[V], Any], V]],
    ) -> "Stream[T, Union[U, V]]":
        """
        Handles any uncaught exceptions that might occur during the execution of the current stream.

        The `handler` function takes an exception as its argument and returns a new value that
        will be used as the output of the stream instead of the exception. The function can also re-raise
        the exception or raise a new one, which will then be propagated further up the stream.

        If an exception occurs in the `handler` function itself, it will be propagated without any
        further handling.

        Example:

        >>> from langstream import Stream, join_final_output
        >>> import asyncio
        ...
        >>> def failed_greeting(name: str):
        ...     raise Exception(f"Giving {name} a cold shoulder")
        ...
        >>> async def example():
        ...     greet_stream = Stream[str, str](
        ...         "GreetingStream",
        ...         failed_greeting
        ...     ).on_error(lambda e: f"Sorry, an error occurred: {str(e)}")
        ...
        ...     async for output in greet_stream("Alice"):
        ...         print(output)
        ...
        >>> asyncio.run(example())
        StreamOutput(stream='GreetingStream', data=Exception('Giving Alice a cold shoulder'), final=False)
        StreamOutput(stream='GreetingStream@on_error', data='Sorry, an error occurred: ...', final=True)
        """

        next_name = f"{self.name}@on_error"
        if hasattr(next, "name"):
            next_name = next.name

        async def on_error(
            input: T,
        ) -> AsyncGenerator[StreamOutput[Union[U, V]], Any]:
            try:
                async for output in self(input):
                    yield cast(StreamOutput[Union[U, V]], output)
            except Exception as e:
                yield cast(StreamOutput[Union[U, V]], self._output_wrap(e, final=False))
                async for output in self._wrap(handler(e), name=next_name):
                    yield cast(StreamOutput[Union[U, V]], output)

        return Stream[T, Union[U, V]](next_name, lambda input: on_error(input))


class SingleOutputStream(Stream[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[StreamOutput[U], Any], AsyncGenerator[U, Any], U]
    ]

    async def _reyield(
        self, async_iterable: AsyncGenerator[StreamOutput[U], Any]
    ) -> AsyncGenerator[Tuple[Optional[U], StreamOutput[U]], Any]:
        final_value: Optional[U] = None
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                final_value = u.data
            yield (final_value, u_rewrapped)

    def map(self, fn: Callable[[U], V]) -> "SingleOutputStream[T, V]":
        """
        Similar to `Stream.map`, this method applies a function to the final output of the stream, but returns a SingleOutputStream.

        The `fn` parameter is a function that takes a value of type U and returns a value of type V.

        For detailed examples, refer to the documentation of `Stream.map`.
        """

        next_name = f"{self.name}@map"

        async def map(input: T) -> AsyncGenerator[StreamOutput[V], Any]:
            # Reyield previous stream so we never block the stream, and at the same time yield mapped values
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[V], to_reyield)
                final_u = value

            yield self._output_wrap(fn(unwrap(final_u)), name=next_name)

        return SingleOutputStream[T, V](next_name, lambda input: map(input))

    def filter(self, fn: Callable[[U], bool]) -> "SingleOutputStream[T, Union[U, None]]":
        """
        Similar to `Stream.filter`, however, singe SingleOutputStream must always produce a value, this method simply replaces
        the value with a None if the filter function returns False

        The `fn` parameter is a function that takes a value of type U and returns a bool.

        Example:

        >>> from langstream import Stream, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     numbers_stream = Stream[int, int]("NumbersStream", lambda input: as_async_generator(*range(0, input)))
        ...     even_stream = numbers_stream.collect().filter(lambda numbers: all([n % 2 == 0 for n in numbers]))
        ...     return await collect_final_output(even_stream(9))
        ...
        >>> asyncio.run(example())
        [None]
        """
        next_name = f"{self.name}@filter"

        async def filter(input: T) -> AsyncGenerator[StreamOutput[Union[U, None]], Any]:
            # Reyield previous stream so we never block the stream, and at the same time yield filtered values
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[Union[U, None]], to_reyield)
                final_u = value

            yield self._output_wrap(
                final_u if fn(unwrap(final_u)) else None, name=next_name
            )

        return SingleOutputStream[T, Union[U, None]](
            next_name, lambda input: filter(input)
        )

    def and_then(
        self,
        next: Callable[
            [U],
            Union[AsyncGenerator[StreamOutput[V], Any], AsyncGenerator[V, Any], V],
        ],
    ) -> "Stream[T, V]":
        """
        Similar to `Stream.and_then`, this method takes a function that receives the final output of this stream as its input and returns a new Stream.

        For detailed examples, refer to the documentation of `Stream.and_then`.
        """
        next_name = f"{self.name}@and_then"
        if hasattr(next, "name"):
            next_name = next.name

        async def and_then(
            input: T,
        ) -> AsyncGenerator[StreamOutput[V], Any]:
            # First, reyield previous stream so we never block the stream, and collect the last result when it is done
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[V], to_reyield)
                final_u = value

            # Then, call in the next stream
            iter_v = self._wrap(next(unwrap(final_u)), name=next_name)
            async for v in iter_v:
                yield v

        return Stream[T, V](next_name, and_then)

    def pipe(
        self,
        fn: Callable[
            [AsyncGenerator[U, Any]], AsyncGenerator[Union[StreamOutput[V], V], Any]
        ],
    ) -> "Stream[T, V]":
        """
        Similar to `Stream.pipe`, except that it takes a stream that will only even produce a single value, so it effectively works basically the same as `and_then`, only with a different interface.

        For detailed examples, refer to the documentation of `Stream.pipe`.
        """
        next_name = f"{self.name}@pipe"
        if hasattr(next, "name"):
            next_name = next.name

        async def pipe(
            input: T,
        ) -> AsyncGenerator[StreamOutput[V], Any]:
            # First, reyield previous stream so we never block the stream, and collect the last result when it is done
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input)):
                yield cast(StreamOutput[V], to_reyield)
                final_u = value

            # Then, call in the piping function
            single_item_stream = as_async_generator(unwrap(final_u))
            iter_v = self._wrap(fn(single_item_stream), name=next_name)
            async for v in iter_v:
                yield cast(StreamOutput[V], v)

        return Stream[T, V](next_name, pipe)

    def gather(
        self: "Union[SingleOutputStream[T, List[AsyncGenerator[StreamOutput[V], Any]]], SingleOutputStream[T, List[AsyncGenerator[V, Any]]]]",
    ) -> "SingleOutputStream[T, List[List[V]]]":
        """
        Similar to `Stream.gather`, this method waits for all the async generators in the list returned by the stream to finish and gathers their results in a list.

        For detailed examples, refer to the documentation of `Stream.gather`.
        """

        next_name = f"{self.name}@gather"

        async def gather(
            input: T,
        ) -> AsyncGenerator[StreamOutput[List[List[V]]], Any]:
            # First, reyield previous stream so we never block the stream, and collect the last result when it is done
            final_u: Optional[
                Union[
                    List[AsyncGenerator[StreamOutput[V], Any]],
                    List[AsyncGenerator[V, Any]],
                ]
            ] = None

            # TODO: try to work out why the type signature of self(input) is not fitting in there, it should
            async for value, to_reyield in self._reyield(cast(Any, self(input))):
                yield cast(StreamOutput[List[List[V]]], to_reyield)
                final_u = value

            if final_u is None:
                final_u = []

            async def consume_async_generator(
                generator: AsyncGenerator[X, Any],
            ) -> Iterable[X]:
                return [item async for item in generator]

            # TODO: should we really wait for everything to arrive before calling asyncio gather? Can we call it during the previous reyield?
            vss: Union[
                List[List[StreamOutput[V]]], List[List[V]]
            ] = await asyncio.gather(*(consume_async_generator(gen) for gen in final_u))

            clean_vss: List[List[V]] = []
            for vs in vss:
                clean_vs: List[V] = []
                for v in vs:
                    v_rewrapped = cast(
                        StreamOutput[List[List[V]]],
                        self._output_wrap(v, final=False),
                    )
                    if isinstance(v, StreamOutput):
                        yield v_rewrapped
                        if v.final:
                            clean_vs.append(v.data)
                    else:
                        clean_vs.append(v)
                clean_vss.append(clean_vs)

            yield self._output_wrap(clean_vss, name=next_name)

        return SingleOutputStream[T, List[List[V]]](next_name, gather)

    def on_error(
        self,
        handler: Callable[[Exception], Union[AsyncGenerator[StreamOutput[V], Any], V]],
    ) -> "SingleOutputStream[T, Union[U, V]]":
        """
        Similar to `Stream.on_error`, this method handles any uncaught exceptions that might occur during the execution of the current stream.

        For detailed examples, refer to the documentation of `Stream.gather`.
        """

        next_name = f"{self.name}@on_error"
        if hasattr(next, "name"):
            next_name = next.name

        async def on_error(
            input: T,
        ) -> AsyncGenerator[StreamOutput[Union[U, V]], Any]:
            try:
                async for output in self(input):
                    yield cast(StreamOutput[Union[U, V]], output)
            except Exception as e:
                async for output in self._wrap(handler(e), name=next_name):
                    yield cast(StreamOutput[Union[U, V]], output)

        return SingleOutputStream[T, Union[U, V]](
            next_name, lambda input: on_error(input)
        )
