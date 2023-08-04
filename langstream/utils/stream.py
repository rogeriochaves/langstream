"""
Utils for working with Streams outputs
"""
from typing import Any, AsyncGenerator, Callable, Iterable, TypeVar, cast

from colorama import Fore

from langstream.core.stream import Stream, StreamOutput
from langstream.utils.async_generator import collect, join

T = TypeVar("T")
U = TypeVar("U")


def debug(
    stream: Callable[[T], AsyncGenerator[StreamOutput[U], Any]]
) -> Stream[T, U]:
    """
    A helper for helping you debugging streams. Simply wrap any piece of the stream or the whole stream together
    with the `debug` function to print out everything that goes through it and its nested streams.

    For example, you can wrap the whole stream to debug everything:
    >>> from langstream import Stream, join_final_output
    >>> import asyncio
    ...
    >>> async def debug_whole_stream():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
    ...     polite_stream = Stream[str, str]("PoliteStream", lambda greeting: f"{greeting} How are you?")
    ...     stream = debug(
    ...         greet_stream.join().and_then(polite_stream)
    ...     )
    ...     await join_final_output(stream("Alice"))
    ...
    >>> asyncio.run(debug_whole_stream())
    <BLANKLINE>
    <BLANKLINE>
    \x1b[32m> GreetingStream\x1b[39m
    <BLANKLINE>
    Hello, Alice!
    <BLANKLINE>
    \x1b[32m> PoliteStream\x1b[39m
    <BLANKLINE>
    Hello, Alice! How are you?

    Or, alternatively, you can debug just a piece of it:
    >>> from langstream import Stream, join_final_output
    >>> import asyncio
    ...
    >>> async def debug_whole_stream():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
    ...     polite_stream = Stream[str, str]("PoliteStream", lambda greeting: f"{greeting} How are you?")
    ...     stream = debug(greet_stream).join().and_then(polite_stream)
    ...     await join_final_output(stream("Alice"))
    ...
    >>> asyncio.run(debug_whole_stream())
    <BLANKLINE>
    <BLANKLINE>
    \x1b[32m> GreetingStream\x1b[39m
    <BLANKLINE>
    Hello, Alice!
    """

    async def debug(input: T) -> AsyncGenerator[StreamOutput[U], Any]:
        last_stream = ""
        last_output = ""
        async for output in stream(input):
            if output.stream != last_stream and last_output == output.data:
                yield output
                continue

            if output.stream != last_stream:
                print("\n", end="", flush=True)
                last_stream = output.stream
                print(f"\n{Fore.GREEN}> {output.stream}{Fore.RESET}\n")
            if hasattr(output.data, "__stream_debug__"):
                output.data.__stream_debug__() # type: ignore
            elif isinstance(output.data, Exception):
                print(f"{Fore.RED}Exception:{Fore.RESET} {output.data}", end="")
            else:
                print(
                    output.data,
                    end=("" if isinstance(output.data, str) else ", "),
                    flush=True,
                )
            last_output = output.data
            yield output

    next_name = f"@debug"
    if hasattr(next, "name"):
        next_name = f"{next.name}@debug"
    return Stream[T, U](next_name, debug)


async def filter_final_output(
    async_iterable: AsyncGenerator[StreamOutput[T], Any]
) -> AsyncGenerator[T, Any]:
    """
    Filters only the final output values of a Stream's outputs.

    Example
    -------
    >>> from langstream import Stream, filter_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
    ...     polite_stream = greet_stream.map(lambda greeting: f"{greeting} How are you?")
    ...     async for output in polite_stream("Alice"):
    ...         print(output)
    ...
    >>> async def only_final_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: f"Hello, {name}!")
    ...     polite_stream = greet_stream.map(lambda greeting: f"{greeting} How are you?")
    ...     async for final_output in filter_final_output(polite_stream("Alice")):
    ...         print(final_output)
    ...
    >>> asyncio.run(all_outputs())
    StreamOutput(stream='GreetingStream', data='Hello, Alice!', final=False)
    StreamOutput(stream='GreetingStream@map', data='Hello, Alice! How are you?', final=True)
    >>> asyncio.run(only_final_outputs())
    Hello, Alice! How are you?
    """
    async for output in async_iterable:
        if output.final:
            yield cast(T, output.data)


async def collect_final_output(
    async_iterable: AsyncGenerator[StreamOutput[T], Any]
) -> Iterable[T]:
    """
    Blocks the stream until it is done, then joins the final output values into a single list.

    Example
    -------
    >>> from langstream import Stream, as_async_generator, collect_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     async for output in greet_stream("Alice"):
    ...         print(output)
    ...
    >>> async def collected_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     output = await collect_final_output(greet_stream("Alice"))
    ...     print(output)
    ...
    >>> asyncio.run(all_outputs())
    StreamOutput(stream='GreetingStream', data='Hello, ', final=True)
    StreamOutput(stream='GreetingStream', data='Alice', final=True)
    StreamOutput(stream='GreetingStream', data='!', final=True)
    >>> asyncio.run(collected_outputs())
    ['Hello, ', 'Alice', '!']
    """
    return await collect(filter_final_output(async_iterable))


async def join_final_output(
    async_iterable: AsyncGenerator[StreamOutput[str], Any]
) -> str:
    """
    Blocks a string producing stream until it is done, then joins the final output values into a single string.

    Example
    -------
    >>> from langstream import Stream, as_async_generator, join_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     async for output in greet_stream("Alice"):
    ...         print(output)
    ...
    >>> async def joined_outputs():
    ...     greet_stream = Stream[str, str]("GreetingStream", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     output = await join_final_output(greet_stream("Alice"))
    ...     print(output)
    ...
    >>> asyncio.run(all_outputs())
    StreamOutput(stream='GreetingStream', data='Hello, ', final=True)
    StreamOutput(stream='GreetingStream', data='Alice', final=True)
    StreamOutput(stream='GreetingStream', data='!', final=True)
    >>> asyncio.run(joined_outputs())
    Hello, Alice!
    """
    return await join(filter_final_output(async_iterable))
