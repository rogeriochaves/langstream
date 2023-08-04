---
sidebar_position: 4
---

# Composing Streams

If you are familiar with Functional Programming, the Stream follows the [Monad Laws](https://wiki.haskell.org/Monad_laws), this ensures they are composable to build complex application following the Category Theory definitions. Our goal on building LangStream was always to make it truly composable, and this is the best abstraction we know for the job, so we adopted it.

But you don't need to understand any Functional Programming or fancy terms, just to understand the seven basic composition functions below:

## `map()`

This is the simplest one, the [`map()`](pathname:///reference/langstream/index.html#langstream.Stream.map) function transforms the output of a Stream, one token at a time as they arrive. The [`map()`](pathname:///reference/langstream/index.html#langstream.Stream.map) function is non-blocking, since it's processing the outputs as they come, so you shouldn't do heavy processing on it, although you can return asynchronous operations from it to await later.

Here is an example:

```python
from langstream import Stream, as_async_generator, join_final_output
import asyncio

async def example():
    # produces one word at a time
    words_stream = Stream[str, str](
        "WordsStream", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    # uppercases each word and take the first letter
    # highlight-next-line
    accronym_stream = words_stream.map(lambda word: word.upper()[0])

    return await join_final_output(accronym_stream("as soon as possible"))

asyncio.run(example())
#=> 'ASAP'
```

As you can see, the words "as", "soon", "as" and "possible" are generated one at a time, then the `map()` function makes them uppercase and take the first letter, we join the final output later, resulting in ASAP.

Here we are using a basic [`Stream`](pathname:///reference/langstream/index.html#stream), but try to replace it with an [`OpenAICompletionStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAICompletionStream) for example and you will see that the `map()` function and all other composition functions work just the same.

## `and_then()`

The [`and_then()`](pathname:///reference/langstream/index.html#langstream.Stream.and_then) is the true composition function, it's what
allows you to compose two streams together, taking the output of one stream, and using as input for another one. Since generally we want the first stream to be finished to send the input to the next one, for example for building a prompt, the [`and_then()`](pathname:///reference/langstream/index.html#langstream.Stream.and_then) function is blocking, which means it will wait for all tokens
to arrive from Stream A, collect them to a list, and only then call the Stream B.

For example:

```python
from langstream import Stream, as_async_generator, join_final_output
from typing import Iterable
import asyncio

async def example():
    words_stream = Stream[str, str](
        "WordsStream", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    last_word_stream = Stream[Iterable[str], str]("LastWordStream", lambda words: list(words)[-1])

    # highlight-next-line
    stream = words_stream.and_then(last_word_stream)

    return await join_final_output(stream("This is time well spent. DUNE!"))

asyncio.run(example())
#=> 'DUNE!'
```

In this example, `last_word_stream` is a stream that takes only the last word that was generated, it takes an `Iterable[str]` as input and produces `str` (the last word) as output. There is no way for it to predict the last word, so of course it has to wait for the previous stream to finish, and `and_then()` does that.

Also, not always the argument to `and_then()` must be another stream, in this case it's simple enough that it can just be a lambda:

```python
composed_stream = words_stream.and_then(lambda words: list(words)[-1])
```

Then again, it could also be an LLM producing tokens in place of those streams, try it out with an [`OpenAICompletionStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAICompletionStream).

## `filter()`

This is also a very simple one, the [`filter()`](pathname:///reference/langstream/index.html#langstream.Stream.map) function keeps the output values that return `True` for your test function. It it also non-blocking, dropping values from the strem as they arrive. For example:

```python
from langstream import Stream, as_async_generator, collect_final_output
import asyncio

async def example():
    numbers_stream = Stream[int, int]("NumbersStream", lambda input: as_async_generator(*range(0, input)))
    even_stream = numbers_stream.filter(lambda input: input % 2 == 0)
    return await collect_final_output(even_stream(9))

asyncio.run(example())
#=> [0, 2, 4, 6, 8]
```

## `collect()`

The [`collect()`](pathname:///reference/langstream/index.html#langstream.Stream.collect) function blocks a Stream until all the values have been generated, and collects it into a list, kinda like what `and_then()` does under the hood, but it doesn't take another stream as an argument, it takes no arguments, it just blocks the current stream transforming it into from a stream of items, to a single list item.

You can use `collect()` + `map()` to achieve the same as the `and_then()` example above:

```python
from langstream import Stream, as_async_generator, join_final_output
import asyncio

async def example():
    words_stream = Stream[str, str](
        "WordsStream", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    # highlight-next-line
    stream = words_stream.collect().map(lambda words: list(words)[-1])

    return await join_final_output(stream("This is time well spent. DUNE!"))

asyncio.run(example())
#=> 'DUNE!'
```

## `join()`

As you may have noticed, both `and_then()` and `collect()` produces a list of items from the previous stream output, this is because streams may produce any type of values, and a list is universal. However, for LLMs, the most common case is for them to produce `str`, which we want to join together as a final `str`, for that, you can use the [`join()`](pathname:///reference/langstream/index.html#langstream.Stream.join) function.

The `join()` function is also blocking, and it will only work if you stream is producing `str` as output, otherwise it will show you a typing error.

Here is an example:

```python
from langstream import Stream, as_async_generator, join_final_output
import asyncio

async def example():
    pairings_stream = Stream[None, str](
        "PairingsStream", lambda _: as_async_generator("Human ", "and ", "dog")
    )

    # highlight-start
    stream = pairings_stream.join().map(
        lambda pairing: "BEST FRIENDS!" if pairing == "Human and dog" else "meh"
    )
    # highlight-end

    return await join_final_output(stream(None))

asyncio.run(example())
#=> 'BEST FRIENDS!'
```

It is common practice to `join()` an LLM output before injecting it as another LLM input.

## `gather()`

Now, for the more advanced use case. Sometimes you want to call not one, but many LLMs at the same time in parallel, for example if you have a series of documents and you want to summarize and score them all, at the same time, to later decide which one is the best document. To create multiple processings, you can use `map()`, but then to wait on them all to finish, you have to use [`gather()`](pathname:///reference/langstream/index.html#langstream.Stream.gather).

The [`gather()`](pathname:///reference/langstream/index.html#langstream.Stream.gather) function works similarly to [`asyncio.gather`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather), but instead of async functions, it can be executed on a stream that is generating other `AsyncGenerator`s (a stream of streams), it will process all those async generators at the same time in parallel and block until they all finish, then it will produce a `List` of `List`s with all the results.

For example:

```python
from langstream import Stream, as_async_generator, collect_final_output
from typing import AsyncGenerator
import asyncio

async def delayed_output(x) -> AsyncGenerator[str, None]:
    await asyncio.sleep(1)
    yield f"Number: {x}"

async def example():
    number_stream = Stream[int, int](
        "NumberStream", lambda x: as_async_generator(*range(x))
    )
    gathered_stream : Stream[int, str] = (
        number_stream.map(delayed_output)
        .gather()
        .and_then(lambda results: as_async_generator(*(r[0] for r in results)))
    )
    return await collect_final_output(gathered_stream(1))

asyncio.run(example()) # will take 1s to finish, not 3s, because it runs in parallel
#=> ['Number: 0', 'Number: 1', 'Number: 2']
```

In this simple example, we generate a range of numbers `[0, 1, 2]`, then for each of those, we simulate a heavy process that would take 1s to finish the `delayed_output`, we `map()` each number to this `delayed_output` function, which is a function that produces an `AsyncGenerator`, then we `gather()`, and then we take the first item of each.

Because we used `gather()`, the stream will take `1s` to finish, because even though each one of the three numbers alone take `1s`, they are ran in parallel, so they finish all together.

## `pipe()`

The [`pipe()`](pathname:///reference/langstream/index.html#langstream.Stream.pipe) gives you a more lower-level composition, it actually gives you the underlying `AsyncGenerator` stream and expects that you
return another `AsyncGenerator` from there, the advantage of that is that you have really fine control, you can for example have something that is blocking and non-blocking at the same time:

```python
from langstream import Stream, as_async_generator, collect_final_output
from typing import List, AsyncGenerator
import asyncio

async def example(items):
    async def mario_pipe(stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
       waiting_for_mushroom = False
       async for item in stream:
           if item == "Mario":
               waiting_for_mushroom = True
           elif item == "Mushroom" and waiting_for_mushroom:
               yield "Super Mario!"
           else:
               yield item + "?"

    piped_stream = Stream[List[str], str](
        "PipedStream", lambda items: as_async_generator(*items)
    ).pipe(mario_pipe)

    return await collect_final_output(piped_stream(items))

asyncio.run(example(["Mario", "Mushroom"]))
#=> ['Super Mario!']

asyncio.run(example(["Luigi"]))
#=> ['Luigi?']

asyncio.run(example(["Mario", "Luigi", "Mushroom"]))
#=> ['Luigi?', 'Super Mario!']
```

As you can see this pipe blocks kinda like `and_then` when it sees "Mario", until a mushroom arrives, but for other random items
such as "Luigi" it just re-yields it immediately, adding a question mark, non-blocking, like `map`. In fact, you can use just
`pipe` to reconstruct `map`, `filter` and `and_then`!

You can also call another stream from `pipe` directly, just be sure to re-yield its outputs

## Standard nomenclature

Now that you know the basic composing functions, it's also interesting to note everything in LangStream also follow the same patterns, for example, for the final output we have the utilities [`filter_final_output()`](pathname:///reference/langstream/index.html#langstream.filter_final_output), [`collect_final_output()`](pathname:///reference/langstream/index.html#langstream.collect_final_output) and [`join_final_output()`](pathname:///reference/langstream/index.html#langstream.join_final_output), you can see they are using the same `filter`, `collect` and `join` names, and they work as you would expect them to.

Now, that you know how to transform and compose streams, keep on reading to understand why type signatures are important to LangStream.
