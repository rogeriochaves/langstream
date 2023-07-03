"""
🪽🔗 LiteChain

This is the top level module for [LiteChain](https://github.com/rogeriochaves/litechain),
all the core classes and functions are made available to be imported from here:

>>> from litechain import Chain, as_async_generator, filter_final_output # etc

Chain
=====

The `Chain` is the core concept of LiteChain for working with LLMs (Large Language Models), it
provides a way to create composable calls to LLMs and any other processing elements.

Since LLMs produce one token at a time, chains are essentially Python AsyncGenerators under the
hood, with type-safe composable functions on top. By making use of the type hints and the
composable functions, LiteChain makes it very easy to build and debug a complex chain of execution
for working with LLMs.

Since async generation streams is the fundamental block of LiteChain, it's processing should never be blocking.
When executing a Chain with input, you get back an AsyncGenerator that produces the outputs of all
pieces in the whole Chain, not only the final one. This means you have access to the each step of
what is happening, making it easier to display and debug. The final output at the edge of the chain
is marked as `final` when you process the Chain stream, with helpers available to filter them.

On this module, we document the low-level concepts of Chains, so we use simple examples of hardcoded
string generation. But one you learn the composition fundamentals here, you can expect to apply the
same functions for composing everythere in LiteChain.

Core Concepts
-------------

`Chain`:
    A Chain takes in a name and a function, which takes an input and produces an asynchronous stream of outputs from it (AsyncGenerator).
    Chains can be chained together with the composition methods below, and their input and output types can be
    specifying in the type signature.

`SingleOutputChain`:
    A SingleOutputChain is a subtype of Chain that produces a single asynchronous final output after processing,
    rather than an asynchronous stream of outputs.

Composition Methods
------------------

`Chain.map`:
    Transforms the output of the Chain by applying a function to each token as they arrive. This is
    non-blocking and maps as chain generations flow in: `chain.map(lambda token: token.lower())`

`Chain.and_then`:
    Applies a function on the list of results of the Chain. Differently from `map`, this is blocking,
    and collects the outputs before applying the function. It can also take another Chain as argument,
    effectively composing two Chains together: `first_chain.and_then(second_chain)`.

`Chain.collect`:
    Collects the output of a Chain into a list. This is a blocking operation and can be used
    when the next processing step requires the full output at once.

`Chain.join`:
    Joins the output of a string producing Chain into a single string by concatenating each item.

`Chain.gather`:
    Gathers results from a chain that produces multiple async generators and processes them in parallel,
    returning a list of lists of the results of all generators, allowing you to execute many Chains at
    the same time, this is similar to `asyncio.gather`.

Contrib: OpenAI, GPT4All and more
---------------------------------

The core of LiteChain is kept small and stable, so all the integrations that build on top of it live separate,
under the `litechain.contrib` module. Check it out for reference and code examples of the integrations.

Examples
--------

Using Chain to process text data:

    >>> from litechain import Chain, as_async_generator, collect_final_output
    >>> import asyncio
    ...
    >>> async def example():
    ...     # Chain that splits a sentence into words
    ...     words_chain = Chain[str, str]("WordsChain", lambda sentence: as_async_generator(*sentence.split(" ")))
    ...     # Chain that capitalizes each word
    ...     capitalized_chain = words_chain.map(lambda word: word.capitalize())
    ...     # Join the capitalized words into a single string
    ...     chain = capitalized_chain.join(" ")
    ...
    ...     async for output in chain("this is an example"):
    ...         if output.final:
    ...             return output.data
    ...
    >>> asyncio.run(example())
    'This Is An Example'

---

Here you can find the reference and code examples, for further tutorials and use cases, consult the [documentation](https://github.com/rogeriochaves/litechain).
"""

from litechain.core.chain import Chain, ChainOutput, SingleOutputChain
from litechain.utils.chain import (
    debug,
    filter_final_output,
    collect_final_output,
    join_final_output,
)
from litechain.utils.async_generator import (
    as_async_generator,
    collect,
    join,
    gather,
    next_item,
)

__all__ = (
    "Chain",
    "ChainOutput",
    "SingleOutputChain",
    "debug",
    "filter_final_output",
    "collect_final_output",
    "join_final_output",
    "as_async_generator",
    "collect",
    "join",
    "gather",
    "next_item",
)
