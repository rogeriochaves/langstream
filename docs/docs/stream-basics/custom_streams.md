---
sidebar_position: 7
---

# Custom Streams

If you have been following the guides, now you know how to create streams, how to compose them together, and everything, however, what if you want to change the core behaviour of the stream, how do you do it? Well, turns out, **there are no "custom streams" really**, it's all just composition.

For example, let's say you want a stream that retries on error, using the [`@retry`](https://pypi.org/project/retry/) library annotation, you can simply create a function that wraps the stream to be retried:

```python
from langstream import Stream
from retry import retry
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")

def retriable(stream: Stream[T, U]) -> Stream[T, U]:
    @retry(tries=3)
    def call_wrapped_stream(input: T):
        return stream(input)

    return Stream[T, U]("RetriableStream", call_wrapped_stream)
```

And use it like this:

```python
from langstream import collect_final_output

attempts = 0

def division_by_attempts(input: int):
    global attempts
    attempts += 1
    return input / (attempts - 1)

stream = retriable(
  Stream[int, float]("BrokenStream", division_by_attempts)
).map(lambda x: x + 1)

await collect_final_output(stream(25))
#=> [26]
```

This stream will first divide by zero, causing a `ZeroDivisionError`, but thanks to our little `retriable` wrapper, it will try again an succeed next time, returning `26`.

So that's it, because streams are just input and output, a simple function will do, if you want to write a class to fit more the type system and be more pythonic, you also can, and the only method you need to override is `__init__`:

```python
class RetriableStream(Stream[T, U]):
    def __init__(self, stream: Stream[T, U], tries=3):
        @retry(tries=tries)
        def call_wrapped_stream(input: T):
            return stream(input)

        super().__init__("RetriableStream", call_wrapped_stream)
```

This will work exactly the same as the function:

```python
attempts = 0

stream = RetriableStream(
  Stream[int, float]("BrokenStream", division_by_attempts)
).map(lambda x: x + 1)

await collect_final_output(stream(25))
#=> [26]
```

As a proof that this is enough, take a look at [how the OpenAICompletionStream is implemented](https://github.com/rogeriochaves/langstream/blob/main/langstream/contrib/llms/open_ai.py#L26), it's a simple wrapper of OpenAI's API under `__init__` and that's it.

## Next Steps

This concludes the guides for Stream Basics, congratulations! On the next steps, we are going to build some real application with real LLMs, stay tuned!
