---
sidebar_position: 6
---

# Error Handling

When dealing with LLMs, errors are actually quite common, be it a connection failure on calling APIs or invalid parameters hallucinated by the model, so it's important to think carefully on how to handle exceptions.

To help with that, LangStream provides an [`on_error`](pathname:///reference/langstream/index.html#langstream.Stream.on_error) method on streams which allows you to capture any unhandled exceptions mid-stream.

The `on_error` function takes a lambda with an exception as its argument and returns a new value that will be used as the output of the stream instead of the exception, you can also call another stream from within the `on_error` handler.

Here is a simple example:

```python
from langstream import Stream

def failed_greeting(name: str):
    raise Exception(f"Giving {name} a cold shoulder")

async def example():
    greet_stream = Stream[str, str](
        "GreetingStream",
        failed_greeting
    ).on_error(lambda e: f"Sorry, an error occurred: {str(e)}")

    async for output in greet_stream("Alice"):
        print(output)

await example()
# StreamOutput(stream='GreetingStream', data=Exception('Giving Alice a cold shoulder'), final=False)
# StreamOutput(stream='GreetingStream@on_error', data='Sorry, an error occurred: Giving Alice a cold shoulder', final=True)
```

You can then keep composing streams after the `on_error`, using methods like `map` or `and_then` after it.

For a more complete example, check out the [Weather Bot with Error Handling](../examples/weather-bot-error-handling) example.

Now go to the next step to figure out how to build your own custom streams!