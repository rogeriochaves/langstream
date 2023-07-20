"""
Utils for working with Chains outputs
"""
from typing import Any, AsyncGenerator, Callable, Iterable, TypeVar, cast

from colorama import Fore

from litechain.core.chain import Chain, ChainOutput
from litechain.utils.async_generator import collect, join

T = TypeVar("T")
U = TypeVar("U")


def debug(
    chain: Callable[[T], AsyncGenerator[ChainOutput[U], Any]]
) -> Chain[T, U]:
    """
    A helper for helping you debugging chains. Simply wrap any piece of the chain or the whole chain together
    with the `debug` function to print out everything that goes through it and its nested chains.

    For example, you can wrap the whole chain to debug everything:
    >>> from litechain import Chain, join_final_output
    >>> import asyncio
    ...
    >>> async def debug_whole_chain():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
    ...     polite_chain = Chain[str, str]("PoliteChain", lambda greeting: f"{greeting} How are you?")
    ...     chain = debug(
    ...         greet_chain.join().and_then(polite_chain)
    ...     )
    ...     await join_final_output(chain("Alice"))
    ...
    >>> asyncio.run(debug_whole_chain())
    <BLANKLINE>
    <BLANKLINE>
    \x1b[32m> GreetingChain\x1b[39m
    <BLANKLINE>
    Hello, Alice!
    <BLANKLINE>
    \x1b[32m> PoliteChain\x1b[39m
    <BLANKLINE>
    Hello, Alice! How are you?

    Or, alternatively, you can debug just a piece of it:
    >>> from litechain import Chain, join_final_output
    >>> import asyncio
    ...
    >>> async def debug_whole_chain():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
    ...     polite_chain = Chain[str, str]("PoliteChain", lambda greeting: f"{greeting} How are you?")
    ...     chain = debug(greet_chain).join().and_then(polite_chain)
    ...     await join_final_output(chain("Alice"))
    ...
    >>> asyncio.run(debug_whole_chain())
    <BLANKLINE>
    <BLANKLINE>
    \x1b[32m> GreetingChain\x1b[39m
    <BLANKLINE>
    Hello, Alice!
    """

    async def debug(input: T) -> AsyncGenerator[ChainOutput[U], Any]:
        last_chain = ""
        last_output = ""
        async for output in chain(input):
            if output.chain != last_chain and last_output == output.data:
                yield output
                continue

            if output.chain != last_chain:
                print("\n", end="", flush=True)
                last_chain = output.chain
                print(f"\n{Fore.GREEN}> {output.chain}{Fore.RESET}\n")
            if hasattr(output.data, "__chain_debug__"):
                output.data.__chain_debug__() # type: ignore
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
    return Chain[T, U](next_name, debug)


async def filter_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T], Any]
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
    ChainOutput(chain='GreetingChain', data='Hello, Alice!', final=False)
    ChainOutput(chain='GreetingChain@map', data='Hello, Alice! How are you?', final=True)
    >>> asyncio.run(only_final_outputs())
    Hello, Alice! How are you?
    """
    async for output in async_iterable:
        if output.final:
            yield cast(T, output.data)


async def collect_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T], Any]
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
    ChainOutput(chain='GreetingChain', data='Hello, ', final=True)
    ChainOutput(chain='GreetingChain', data='Alice', final=True)
    ChainOutput(chain='GreetingChain', data='!', final=True)
    >>> asyncio.run(collected_outputs())
    ['Hello, ', 'Alice', '!']
    """
    return await collect(filter_final_output(async_iterable))


async def join_final_output(
    async_iterable: AsyncGenerator[ChainOutput[str], Any]
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
    ChainOutput(chain='GreetingChain', data='Hello, ', final=True)
    ChainOutput(chain='GreetingChain', data='Alice', final=True)
    ChainOutput(chain='GreetingChain', data='!', final=True)
    >>> asyncio.run(joined_outputs())
    Hello, Alice!
    """
    return await join(filter_final_output(async_iterable))
