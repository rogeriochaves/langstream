---
sidebar_position: 6
---

# Error Handling

When dealing with LLMs, errors are actually quite common, be it a connection failure on calling APIs or invalid parameters hallucinated by the model, so it's important to think carefully on how to handle exceptions.

To help with that, LiteChain provides an [`on_error`](pathname:///reference/litechain/index.html#litechain.Chain.on_error) method on chains which allows you to capture any unhandled exceptions mid-chain.

The `on_error` function takes a lambda with an exception as its argument and returns a new value that will be used as the output of the chain instead of the exception, you can also call another chain from within the `on_error` handler.

Here is a simple example:

```python
from litechain import Chain

def failed_greeting(name: str):
    raise Exception(f"Giving {name} a cold shoulder")

async def example():
    greet_chain = Chain[str, str](
        "GreetingChain",
        failed_greeting
    ).on_error(lambda e: f"Sorry, an error occurred: {str(e)}")

    async for output in greet_chain("Alice"):
        print(output)

await example()
# ChainOutput(chain='GreetingChain', data=Exception('Giving Alice a cold shoulder'), final=False)
# ChainOutput(chain='GreetingChain@on_error', data='Sorry, an error occurred: Giving Alice a cold shoulder', final=True)
```

You can then keep composing chains after the `on_error`, using methods like `map` or `and_then` after it.

For a more complete example, check out the [Weather Bot with Error Handling](../examples/weather-bot-error-handling) example.

## Next Steps

This concludes the guides for Chain Basics, congratulations! On the next steps, we are going to build some real application with real LLMs, stay tuned!
