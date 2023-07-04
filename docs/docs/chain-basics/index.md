---
sidebar_position: 2
---

# Chain Basics

The [Chain](/reference/litechain/index.html#chain) is the main building block of LiteChain, you compose chains together to build your LLM application.

A Chain is basically a function that takes an input and produces an [AsyncGenerator](https://peps.python.org/pep-0525/) of an output, if you are not familiar with async generators, you can think about it as a stream, or in other word, a list over time.

The simplest of all chains, takes one input and produces a stream of outputs of a single item, and this is how you create one:

```python
uppercase_chain = Chain[str, str]("UppercaseChain", lambda input: input.upper())
```

As you can see, there are some parameters you pass to it, first of all is the type signature `[str, str]`, this defines the input and output types of the chain, respectively. In this case they are the same, but they could be different, you can read more about why
types are important for LiteChain [here](#) (TODO: link pending).

It also takes a name, `"UppercaseChain"`, this can literally be anything you want, the reason for having a name, however, is making it easier to debug, if any issues arrive along the way, you can debug and visualize exactly why chains are misbehaving.

Then, the heart of the chain, is the lambda function that is executed when the chain is called. It takes exactly one input (which is `str` in this) and must return a value of the specified output type (also `str`), here it just returns the same input but in uppercase.

Now that we have a chain, we can just run it, as a function, and we will get back an [AsyncGenerator](https://peps.python.org/pep-0525/) of outputs that we can iterate on. Here is the full example:

```python
from litechain import Chain
import asyncio

async def example():
    uppercase_chain = Chain[str, str]("UppercaseChain", lambda input: input.upper())

    async for output in uppercase_chain("i am not screaming"):
        print(output.data)

asyncio.run(example())
#=> I AM NOT SCREAMING
```

As you can see, upon calling the chain, we had to iterate over it using `async for`, this loop will only run once, because our chain is producing a single value, but still, it is necessary since chains are always producing async generators.
Go to the next section to understand better why is that.