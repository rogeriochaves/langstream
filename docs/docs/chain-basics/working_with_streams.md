---
sidebar_position: 3
---

# Working with Streams

By default, all LLMs generate a stream of tokens:

```python
from litechain.contrib import OpenAICompletionChain

bacon_chain = OpenAICompletionChain[str, str](
    "BaconChain",
    lambda input: input,
    model="ada",
)

async for output in bacon_chain("I like bacon and"):
    print(output.data)
#=> iced
#=>  tea
#=> .
#=>  I
#=>  like
#=>  to
#=>  eat
#=>  bacon
#=>  and
#=>
#=> iced
#=>  tea
#=> .
```

You can notice that it will print more or less one word per line, those are the tokens it is generating, since Python by default adds a new line for each `print` statement, we end up with one token per line.

When creating a simple Chain, if you return a single value, it will also output just that single value, so if you want to simulate an LLM, and create a chain that produces a stream of outputs, you can use the [`as_async_generator()`](pathname:///reference/litechain/index.html#litechain.as_async_generator) utility function:


```python
from litechain import Chain, as_async_generator

stream_of_bacon_chain = Chain[None, str](
    "StreamOfBaconChain",
    lambda _: as_async_generator("I", "like", "bacon"),
)

async for output in stream_of_bacon_chain(None):
    print(output.data)
#=> I
#=> like
#=> bacon
```

## The whole Chain is streamed

On LiteChain, when you compose two or more chains, map the results or apply any operations on it, still the original values of anything generating outputs anywhere in the chain gets streamed, this means that if you have a chain being mapped,
both the original output and the transformed ones will be outputted, for example:

```python
from litechain import Chain, as_async_generator

stream_of_bacon_chain = Chain[None, str](
    "StreamOfBaconChain",
    lambda _: as_async_generator("I", "like", "bacon"),
)

tell_the_world = stream_of_bacon_chain.map(lambda token: token.upper())

async for output in tell_the_world(None):
    print(output.chain, ":", output.data)
#=> StreamOfBaconChain : I
#=> StreamOfBaconChain@map : I
#=> StreamOfBaconChain : like
#=> StreamOfBaconChain@map : LIKE
#=> StreamOfBaconChain : bacon
#=> StreamOfBaconChain@map : BACON
```

This is done by design so that you can always inspect what is going in the middle of a complex chain, either to debug it, or to display to the user for a better user experience.

If you want just the final output, you can check for the property [`output.final`](pathname:///reference/litechain/index.html#litechain.ChainOutput.final):

```python
import time

async for output in tell_the_world(None):
    if output.final:
        time.sleep(1) # added for dramatic effect
        print(output.data)
#=> I
#=> LIKE
#=> BACON
```

## Output Utils

Now, as shown on the examples, you need to iterate over it with `async for` to get the final output. However, you might not care about streaming or inspecting the middle results at all, and just want the final result as a whole. For that, you can use some utility functions that LiteChain provides, for example, [`collect_final_output()`](pathname:///reference/litechain/index.html#litechain.collect_final_output), which gives you a single list with the final outputs all at once:

```python
from litechain import collect_final_output

await collect_final_output(tell_the_world(None))
#=> ['I', 'LIKE', 'BACON']
```

Or, if you chain's final output is `str`, then you can use [`join_final_output()`](pathname:///reference/litechain/index.html#litechain.join_final_output), which gives you already the full string, concatenated

```python
from litechain import join_final_output

await join_final_output(tell_the_world(None))
#=> 'ILIKEBACON'
```

(LLMs produce spaces as token as well, so normally the lack of spaces in here is not a problem)

Check out also [`filter_final_output()`](pathname:///reference/litechain/index.html#litechain.filter_final_output), which gives you still an `AsyncGenerator` to loop over, but including only the final results.

Now that you know all about streams, you need to understand what does that mean when you are composing them together, keep on reading to learn about Composing Chains.