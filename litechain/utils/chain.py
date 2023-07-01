"""
Utils for working with Chains outputs
"""
from typing import Any, AsyncGenerator, Iterable, TypeVar, cast

from litechain.core.chain import ChainOutput
from litechain.utils.async_generator import collect, join

T = TypeVar("T")


async def filter_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T, Any], Any]
) -> AsyncGenerator[T, Any]:
    """
    Filters only the final output values of a Chain's outputs.

    Example
    -------
    >>> from litechain import Chain, filter_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
    ...     polite_chain = greet_chain.map(lambda greeting: f"{greeting} How are you?")
    ...     async for output in polite_chain("Alice"):
    ...         print(output)
    ...
    >>> async def only_final_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
    ...     polite_chain = greet_chain.map(lambda greeting: f"{greeting} How are you?")
    ...     async for final_output in filter_final_output(polite_chain("Alice")):
    ...         print(final_output)
    ...
    >>> asyncio.run(all_outputs())
    ChainOutput(chain='GreetingChain', output='Hello, Alice!', final=False)
    ChainOutput(chain='GreetingChain@map', output='Hello, Alice! How are you?', final=True)
    >>> asyncio.run(only_final_outputs())
    Hello, Alice! How are you?
    """
    async for output in async_iterable:
        if output.final:
            yield cast(T, output.output)


async def collect_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T, Any], Any]
) -> Iterable[T]:
    """
    Blocks the chain until it is done, then joins the final output values into a single list.

    Example
    -------
    >>> from litechain import Chain, as_async_generator, collect_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     async for output in greet_chain("Alice"):
    ...         print(output)
    ...
    >>> async def collected_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     output = await collect_final_output(greet_chain("Alice"))
    ...     print(output)
    ...
    >>> asyncio.run(all_outputs())
    ChainOutput(chain='GreetingChain', output='Hello, ', final=True)
    ChainOutput(chain='GreetingChain', output='Alice', final=True)
    ChainOutput(chain='GreetingChain', output='!', final=True)
    >>> asyncio.run(collected_outputs())
    ['Hello, ', 'Alice', '!']
    """
    return await collect(filter_final_output(async_iterable))


async def join_final_output(
    async_iterable: AsyncGenerator[ChainOutput[str, Any], Any]
) -> str:
    """
    Blocks a string producing chain until it is done, then joins the final output values into a single string.

    Example
    -------
    >>> from litechain import Chain, as_async_generator, join_final_output
    >>> import asyncio
    ...
    >>> async def all_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     async for output in greet_chain("Alice"):
    ...         print(output)
    ...
    >>> async def joined_outputs():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: as_async_generator("Hello, ", name, "!"))
    ...     output = await join_final_output(greet_chain("Alice"))
    ...     print(output)
    ...
    >>> asyncio.run(all_outputs())
    ChainOutput(chain='GreetingChain', output='Hello, ', final=True)
    ChainOutput(chain='GreetingChain', output='Alice', final=True)
    ChainOutput(chain='GreetingChain', output='!', final=True)
    >>> asyncio.run(joined_outputs())
    Hello, Alice!
    """
    return await join(filter_final_output(async_iterable))
