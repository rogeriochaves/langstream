"""
Utils for working with Python's AsyncIterable with the same primitives as chains
"""
import asyncio
from typing import AsyncIterable, List, TypeVar

T = TypeVar("T")


async def collect(async_iterable: AsyncIterable[T]) -> List[T]:
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


async def join(async_iterable: AsyncIterable[str], join_with="") -> str:
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


async def gather(async_iterables: List[AsyncIterable[T]]) -> List[List[T]]:
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
