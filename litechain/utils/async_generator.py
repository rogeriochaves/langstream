"""
Utils for working with Python's AsyncGenerator with the same primitives as chains
"""
import asyncio
from typing import Any, AsyncGenerator, List, TypeVar

T = TypeVar("T")


async def as_async_generator(*values: T) -> AsyncGenerator[T, Any]:
    """
    Creates an asynchronous generator out of simple values, it's useful for
    converting a single value or a list of values to a streamed output of a Chain

    Example
    -------
    >>> import asyncio
    >>> async def run_example():
    ...     async for value in as_async_generator(1, 2, 3):
    ...         print(value)
    ...
    >>> asyncio.run(run_example())
    1
    2
    3
    """
    for item in values:
        yield item


async def collect(async_generator: AsyncGenerator[T, Any]) -> List[T]:
    """
    Collect items from an async generator into a list.

    >>> import asyncio
    >>> async def async_gen():
    ...     yield "hello"
    ...     yield "how"
    ...     yield "can"
    ...     yield "I"
    ...     yield "assist"
    ...     yield "you"
    ...     yield "today"
    >>> asyncio.run(collect(async_gen()))
    ['hello', 'how', 'can', 'I', 'assist', 'you', 'today']
    """
    return [item async for item in async_generator]


async def join(async_generator: AsyncGenerator[str, Any], separator="") -> str:
    """
    Collect items from an async generator and join them in a string.

    >>> import asyncio
    >>> async def async_gen():
    ...     yield "hello "
    ...     yield "how "
    ...     yield "can "
    ...     yield "I "
    ...     yield "assist "
    ...     yield "you "
    ...     yield "today"
    >>> asyncio.run(join(async_gen()))
    'hello how can I assist you today'
    """
    lst = await collect(async_generator)
    return separator.join(lst)


async def gather(async_generators: List[AsyncGenerator[T, Any]]) -> List[List[T]]:
    """
    Gather items from a list of async generators into a list of lists.

    >>> import asyncio
    >>> async def async_gen1():
    ...     yield "hello"
    ...     yield "how"
    ...     yield "can"
    >>> async def async_gen2():
    ...     yield "I"
    ...     yield "assist"
    ...     yield "you"
    ...     yield "today"
    >>> asyncio.run(gather([async_gen1(), async_gen2()]))
    [['hello', 'how', 'can'], ['I', 'assist', 'you', 'today']]
    """
    return await asyncio.gather(*(collect(generator) for generator in async_generators))


async def next_item(async_generator: AsyncGenerator[T, Any]) -> T:
    return await async_generator.__aiter__().__anext__()
