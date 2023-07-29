"""
Utils for working with Python's AsyncGenerator with the same primitives as chains
"""
import asyncio
from typing import Any, AsyncGenerator, List, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


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
    """
    Takes the next item of an AsyncGenerator, can result in exception if there is no items left to be taken

    >>> import asyncio
    >>> async def async_gen():
    ...     yield "hello"
    ...     yield "how"
    ...     yield "are"
    >>> asyncio.run(next_item(async_gen()))
    'hello'
    """
    return await async_generator.__aiter__().__anext__()


# From: https://stackoverflow.com/a/55317623
def merge(
    async_generator_a: AsyncGenerator[T, Any], async_generator_b: AsyncGenerator[U, Any]
) -> AsyncGenerator[Union[T, U], Any]:
    """
    Merges two AsyncGenerators into one, taking values from both generators as soon as they arrive.

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
    >>> async def example():
    ...     return await collect(merge(async_gen1(), async_gen2()))
    >>> asyncio.run(example())
    ['hello', 'how', 'I', 'can', 'assist', 'you', 'today']
    """

    aiters = [async_generator_a, async_generator_b]

    queue = asyncio.Queue(1)
    run_count = len(aiters)
    cancelling = False

    async def drain(aiter):
        nonlocal run_count
        try:
            async for item in aiter:
                await queue.put((False, item))
        except Exception as e:
            if not cancelling:
                await queue.put((True, e))
            else:
                raise
        finally:
            run_count -= 1

    async def merged():
        try:
            while run_count:
                raised, next_item = await queue.get()
                if raised:
                    cancel_tasks()
                    raise next_item
                yield next_item
        finally:
            cancel_tasks()

    def cancel_tasks():
        nonlocal cancelling
        cancelling = True
        for t in tasks:
            t.cancel()

    tasks = [asyncio.create_task(drain(aiter)) for aiter in aiters]
    return merged()
