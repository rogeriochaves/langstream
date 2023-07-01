"""
Utils for working with Python's AsyncGenerator with the same primitives as chains
"""
import asyncio
from typing import Any, AsyncGenerator, List, TypeVar

T = TypeVar("T")


async def as_async_generator(*values: T) -> AsyncGenerator[T, Any]:
    for item in values:
        yield item


async def collect(async_iterable: AsyncGenerator[T, Any]) -> List[T]:
    """
    Collect items from an async iterable into a list.

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
    return [item async for item in async_iterable]


async def join(async_iterable: AsyncGenerator[str, Any], join_with="") -> str:
    """
    Collect items from an async iterable and join them in a string.

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
    lst = await collect(async_iterable)
    return join_with.join(lst)


async def gather(async_iterables: List[AsyncGenerator[T, Any]]) -> List[List[T]]:
    """
    Gather items from a list of async iterables into a list of lists.

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
    return await asyncio.gather(*(collect(iterable) for iterable in async_iterables))


async def next_item(async_iterable: AsyncGenerator[T, Any]) -> T:
    return await async_iterable.__aiter__().__anext__()
