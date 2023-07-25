---
sidebar_position: 7
---

# Custom Chains

If you have been following the guides, now you know how to create chains, how to compose them together, and everything, however, what if you want to change the core behaviour of the chain, how do you do it? Well, turns out, **there are no "custom chains" really**, it's all just composition.

For example, let's say you want a chain that retries on error, using the [`@retry`](https://pypi.org/project/retry/) library annotation, you can simply create a function that wraps the chain to be retried:

```python
from litechain import Chain
from retry import retry
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")

def retriable(chain: Chain[T, U]) -> Chain[T, U]:
    @retry(tries=3)
    def call_wrapped_chain(input: T):
        return chain(input)

    return Chain[T, U]("RetriableChain", call_wrapped_chain)
```

And use it like this:

```python
from litechain import collect_final_output

attempts = 0

def division_by_attempts(input: int):
    global attempts
    attempts += 1
    return input / (attempts - 1)

chain = retriable(
  Chain[int, float]("BrokenChain", division_by_attempts)
).map(lambda x: x + 1)

await collect_final_output(chain(25))
#=> [26]
```

This chain will first divide by zero, causing a `ZeroDivisionError`, but thanks to our little `retriable` wrapper, it will try again an succeed next time, returning `26`.

So that's it, because chains are just input and output, a simple function will do, if you want to write a class to fit more the type system and be more pythonic, you also can, and the only method you need to override is `__init__`:

```python
class RetriableChain(Chain[T, U]):
    def __init__(self, chain: Chain[T, U], tries=3):
        @retry(tries=tries)
        def call_wrapped_chain(input: T):
            return chain(input)

        super().__init__("RetriableChain", call_wrapped_chain)
```

This will work exactly the same as the function:

```python
attempts = 0

chain = RetriableChain(
  Chain[int, float]("BrokenChain", division_by_attempts)
).map(lambda x: x + 1)

await collect_final_output(chain(25))
#=> [26]
```

As a proof that this is enough, take a look at [how the OpenAICompletionChain is implemented](https://github.com/rogeriochaves/litechain/blob/main/litechain/contrib/llms/open_ai.py#L26), it's a simple wrapper of OpenAI's API under `__init__` and that's it.

## Next Steps

This concludes the guides for Chain Basics, congratulations! On the next steps, we are going to build some real application with real LLMs, stay tuned!
