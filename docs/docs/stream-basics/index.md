---
sidebar_position: 2
---

# Stream Basics

The [Stream](pathname:///reference/langstream/index.html#stream) is the main building block of LangStream, you compose streams together to build your LLM application.

A Stream is basically a function that takes an input and produces an [`AsyncGenerator`](https://peps.python.org/pep-0525/) of an output, if you are not familiar with async generators, you can think about it as list over time.

The simplest of all streams takes one input and produces a single item, and this is how you create one:

```python
uppercase_stream = Stream[str, str]("UppercaseStream", lambda input: input.upper())
```

As you can see, there are some parameters you pass to it, first of all is the type signature `[str, str]`, this defines the input and output types of the stream, respectively. In this case they are the same, but they could be different, you can read more about why types are important for LangStream [here](/docs/stream-basics/type_signatures).

It also takes a name, `"UppercaseStream"`, the reason for having a name is making it easier to debug, so it can be anything you want, as long as it's helpful for you to identify later. If any issues arrive along the way, you can debug and visualize exactly which streams are misbehaving.

Then, the heart of the stream, is the lambda function that is executed when the stream is called. It takes exactly one input (which is `str` in this) and must return a value of the specified output type (also `str`), here it just returns the same input but in uppercase.

Now that we have a stream, we can just run it, as a function, and we will get back an [`AsyncGenerator`](https://peps.python.org/pep-0525/) of outputs that we can iterate on. Here is the full example:

```python
from langstream import Stream
import asyncio

async def example():
    uppercase_stream = Stream[str, str]("UppercaseStream", lambda input: input.upper())

    async for output in uppercase_stream("i am not screaming"):
        print(output.data)

asyncio.run(example())
#=> I AM NOT SCREAMING
```

As you can see, upon calling the stream, we had to iterate over it using `async for`, this loop will only run once, because our stream is producing a single value, but still, it is necessary since streams are always producing async generators.
Go to the next section to understand better why is that.