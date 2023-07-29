---
sidebar_position: 4
---

# Composing Chains

If you are familiar with Functional Programming, the Chain follows the [Monad Laws](https://wiki.haskell.org/Monad_laws), this ensures they are composable to build complex application following the Category Theory definitions. Our goal on building LiteChain was always to make it truly composable, and this is the best abstraction we know for the job, so we adopted it.

But you don't need to understand any Functional Programming or fancy terms, just to understand the six basic composition functions below:

## `map()`

This is the simplest one, the [`map()`](pathname:///reference/litechain/index.html#litechain.Chain.map) function transforms the output of a Chain, one token at a time as they arrive. The [`map()`](pathname:///reference/litechain/index.html#litechain.Chain.map) function is non-blocking, since it's processing the outputs as they come, so you shouldn't do heavy processing on it, although you can return asynchronous operations from it to await later.

Here is an example:

```python
from litechain import Chain, as_async_generator, join_final_output
import asyncio

async def example():
    # produces one word at a time
    words_chain = Chain[str, str](
        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    # uppercases each word and take the first letter
    # highlight-next-line
    accronym_chain = words_chain.map(lambda word: word.upper()[0])

    return await join_final_output(accronym_chain("as soon as possible"))

asyncio.run(example())
#=> 'ASAP'
```

As you can see, the words "as", "soon", "as" and "possible" are generated one at a time, then the `map()` function makes them uppercase and take the first letter, we join the final output later, resulting in ASAP.

Here we are using a basic [`Chain`](pathname:///reference/litechain/index.html#chain), but try to replace it with an [`OpenAICompletionChain`](pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAICompletionChain) for example and you will see that the `map()` function and all other composition functions work just the same.

## `and_then()`

The [`and_then()`](pathname:///reference/litechain/index.html#litechain.Chain.and_then) is the true composition function, it's what
allows you to compose two chains together, taking the output of one chain, and using as input for another one. Since generally we want the first chain to be finished to send the input to the next one, for example for building a prompt, the [`and_then()`](pathname:///reference/litechain/index.html#litechain.Chain.and_then) function is blocking, which means it will wait for all tokens
to arrive from Chain A, collect them to a list, and only then call the Chain B.

For example:

```python
from litechain import Chain, as_async_generator, join_final_output
from typing import Iterable
import asyncio

async def example():
    words_chain = Chain[str, str](
        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    last_word_chain = Chain[Iterable[str], str]("LastWordChain", lambda words: list(words)[-1])

    # highlight-next-line
    chain = words_chain.and_then(last_word_chain)

    return await join_final_output(chain("This is time well spent. DUNE!"))

asyncio.run(example())
#=> 'DUNE!'
```

In this example, `last_word_chain` is a chain that takes only the last word that was generated, it takes an `Iterable[str]` as input and produces `str` (the last word) as output. There is no way for it to predict the last word, so of course it has to wait for the previous chain to finish, and `and_then()` does that.

Also, not always the argument to `and_then()` must be another chain, in this case it's simple enough that it can just be a lambda:

```python
composed_chain = words_chain.and_then(lambda words: list(words)[-1])
```

Then again, it could also be an LLM producing tokens in place of those chains, try it out with an [`OpenAICompletionChain`](pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAICompletionChain).

## `collect()`

The [`collect()`](pathname:///reference/litechain/index.html#litechain.Chain.collect) function blocks a Chain until all the values have been generated, and collects it into a list, kinda like what `and_then()` does under the hood, but it doesn't take another chain as an argument, it takes no arguments, it just blocks the current chain transforming it into from a stream of items, to a single list item.

You can use `collect()` + `map()` to achieve the same as the `and_then()` example above:

```python
from litechain import Chain, as_async_generator, join_final_output
import asyncio

async def example():
    words_chain = Chain[str, str](
        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))
    )

    # highlight-next-line
    chain = words_chain.collect().map(lambda words: list(words)[-1])

    return await join_final_output(chain("This is time well spent. DUNE!"))

asyncio.run(example())
#=> 'DUNE!'
```

## `join()`

As you may have noticed, both `and_then()` and `collect()` produces a list of items from the previous chain output, this is because chains may produce any type of values, and a list is universal. However, for LLMs, the most common case is for them to produce `str`, which we want to join together as a final `str`, for that, you can use the [`join()`](pathname:///reference/litechain/index.html#litechain.Chain.join) function.

The `join()` function is also blocking, and it will only work if you chain is producing `str` as output, otherwise it will show you a typing error.

Here is an example:

```python
from litechain import Chain, as_async_generator, join_final_output
import asyncio

async def example():
    pairings_chain = Chain[None, str](
        "PairingsChain", lambda _: as_async_generator("Human ", "and ", "dog")
    )

    # highlight-start
    chain = pairings_chain.join().map(
        lambda pairing: "BEST FRIENDS!" if pairing == "Human and dog" else "meh"
    )
    # highlight-end

    return await join_final_output(chain(None))

asyncio.run(example())
#=> 'BEST FRIENDS!'
```

It is common practice to `join()` an LLM output before injecting it as another LLM input.

## `gather()`

Now, for the more advanced use case. Sometimes you want to call not one, but many LLMs at the same time in parallel, for example if you have a series of documents and you want to summarize and score them all, at the same time, to later decide which one is the best document. To create multiple processings, you can use `map()`, but then to wait on them all to finish, you have to use [`gather()`](pathname:///reference/litechain/index.html#litechain.Chain.gather).

The [`gather()`](pathname:///reference/litechain/index.html#litechain.Chain.gather) function works similarly to [`asyncio.gather`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather), but instead of async functions, it can be executed on a chain that is generating other `AsyncGenerator`s (a chain of chains), it will process all those async generators at the same time in parallel and block until they all finish, then it will produce a `List` of `List`s with all the results.

For example:

```python
from litechain import Chain, as_async_generator, collect_final_output
from typing import AsyncGenerator
import asyncio

async def delayed_output(x) -> AsyncGenerator[str, None]:
    await asyncio.sleep(1)
    yield f"Number: {x}"

async def example():
    number_chain = Chain[int, int](
        "NumberChain", lambda x: as_async_generator(*range(x))
    )
    gathered_chain : Chain[int, str] = (
        number_chain.map(delayed_output)
        .gather()
        .and_then(lambda results: as_async_generator(*(r[0] for r in results)))
    )
    return await collect_final_output(gathered_chain(1))

asyncio.run(example()) # will take 1s to finish, not 3s, because it runs in parallel
#=> ['Number: 0', 'Number: 1', 'Number: 2']
```

In this simple example, we generate a range of numbers `[0, 1, 2]`, then for each of those, we simulate a heavy process that would take 1s to finish the `delayed_output`, we `map()` each number to this `delayed_output` function, which is a function that produces an `AsyncGenerator`, then we `gather()`, and then we take the first item of each.

Because we used `gather()`, the chain will take `1s` to finish, because even though each one of the three numbers alone take `1s`, they are ran in parallel, so they finish all together.

## `pipe()`

The [`pipe()`](pathname:///reference/litechain/index.html#litechain.Chain.pipe) gives you a more lower-level composition, it actually gives you the underlying `AsyncGenerator` stream and expects that you
return another `AsyncGenerator` from there, the advantage of that is that you have really fine control, you can for example have something that is blocking and non-blocking at the same time:

```python
from litechain import Chain, as_async_generator, collect_final_output
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

    piped_chain = Chain[List[str], str](
        "PipedChain", lambda items: as_async_generator(*items)
    ).pipe(mario_pipe)

    return await collect_final_output(piped_chain(items))

asyncio.run(example(["Mario", "Mushroom"]))
#=> ['Super Mario!']

asyncio.run(example(["Luigi"]))
#=> ['Luigi?']

asyncio.run(example(["Mario", "Luigi", "Mushroom"]))
#=> ['Luigi?', 'Super Mario!']
```

As you can see this pipe blocks kinda like `and_then` when it sees "Mario", until a mushroom arrives, but for other random items
such as "Luigi" it just re-yields it immediately, adding a question mark, non-blocking, like `map`. In fact, you can use just
`pipe` to reconstruct both `map` and `and_then`!

You can also call another chain from `pipe` directly, just be sure to re-yield its outputs

## Standard nomenclature

Now that you know the basic composing functions, it's also interesting to note everything in LiteChain also follow the same patterns, for example, for the final output we have the utilities [`filter_final_output()`](pathname:///reference/litechain/index.html#litechain.filter_final_output), [`collect_final_output()`](pathname:///reference/litechain/index.html#litechain.collect_final_output) and [`join_final_output()`](pathname:///reference/litechain/index.html#litechain.join_final_output), you can see they are using the same `filter`, `collect` and `join` names, and they work as you would expect them to.

Now, that you know how to transform and compose chains, keep on reading to understand why type signatures are important to LiteChain.
