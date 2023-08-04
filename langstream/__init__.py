"""
🪽🔗 LangStream

This is the top level module for [LangStream](https://github.com/rogeriochaves/langstream),
all the core classes and functions are made available to be imported from here:

>>> from langstream import Stream, as_async_generator, filter_final_output # etc

Stream
=====

The `Stream` is the core concept of LangStream for working with LLMs (Large Language Models), it
provides a way to create composable calls to LLMs and any other processing elements.

Since LLMs produce one token at a time, streams are essentially Python AsyncGenerators under the
hood, with type-safe composable functions on top. By making use of the type hints and the
composable functions, LangStream makes it very easy to build and debug a complex stream of execution
for working with LLMs.

Since async generation streams is the fundamental block of LangStream, it's processing should never be blocking.
When executing a Stream with input, you get back an AsyncGenerator that produces the outputs of all
pieces in the whole Stream, not only the final one. This means you have access to the each step of
what is happening, making it easier to display and debug. The final output at the edge of the stream
is marked as `final` when you process the Stream stream, with helpers available to filter them.

On this module, we document the low-level concepts of Streams, so we use simple examples of hardcoded
string generation. But one you learn the composition fundamentals here, you can expect to apply the
same functions for composing everythere in LangStream.

Core Concepts
-------------

`Stream`:
    A Stream takes in a name and a function, which takes an input and produces an asynchronous stream of outputs from it (AsyncGenerator).
    Streams can be streamed together with the composition methods below, and their input and output types can be
    specifying in the type signature.

`SingleOutputStream`:
    A SingleOutputStream is a subtype of Stream that produces a single asynchronous final output after processing,
    rather than an asynchronous stream of outputs.

Composition Methods
------------------

`Stream.map`:
    Transforms the output of the Stream by applying a function to each token as they arrive. This is
    non-blocking and maps as stream generations flow in: `stream.map(lambda token: token.lower())`

`Stream.and_then`:
    Applies a function on the list of results of the Stream. Differently from `map`, this is blocking,
    and collects the outputs before applying the function. It can also take another Stream as argument,
    effectively composing two Streams together: `first_stream.and_then(second_stream)`.

`Stream.collect`:
    Collects the output of a Stream into a list. This is a blocking operation and can be used
    when the next processing step requires the full output at once.

`Stream.join`:
    Joins the output of a string producing Stream into a single string by concatenating each item.

`Stream.gather`:
    Gathers results from a stream that produces multiple async generators and processes them in parallel,
    returning a list of lists of the results of all generators, allowing you to execute many Streams at
    the same time, this is similar to `asyncio.gather`.

Contrib: OpenAI, GPT4All and more
---------------------------------

The core of LangStream is kept small and stable, so all the integrations that build on top of it live separate,
under the `langstream.contrib` module. Check it out for reference and code examples of the integrations.

Examples
--------

Using Stream to process text data:

    >>> from langstream import Stream, as_async_generator, collect_final_output
    >>> import asyncio
    ...
    >>> async def example():
    ...     # Stream that splits a sentence into words
    ...     words_stream = Stream[str, str]("WordsStream", lambda sentence: as_async_generator(*sentence.split(" ")))
    ...     # Stream that capitalizes each word
    ...     capitalized_stream = words_stream.map(lambda word: word.capitalize())
    ...     # Join the capitalized words into a single string
    ...     stream = capitalized_stream.join(" ")
    ...
    ...     async for output in stream("this is an example"):
    ...         if output.final:
    ...             return output.data
    ...
    >>> asyncio.run(example())
    'This Is An Example'

---

Here you can find the reference and code examples, for further tutorials and use cases, consult the [documentation](https://github.com/rogeriochaves/langstream).
"""

from langstream.core.stream import Stream, StreamOutput, SingleOutputStream
from langstream.utils.stream import (
    debug,
    filter_final_output,
    collect_final_output,
    join_final_output,
)
from langstream.utils.async_generator import (
    as_async_generator,
    collect,
    join,
    gather,
    next_item,
)

__all__ = (
    "Stream",
    "StreamOutput",
    "SingleOutputStream",
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
