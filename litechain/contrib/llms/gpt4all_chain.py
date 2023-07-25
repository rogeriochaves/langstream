import asyncio
from typing import AsyncGenerator, Callable, Iterable, Optional, TypeVar, cast

from gpt4all import GPT4All

from litechain.core.chain import Chain

T = TypeVar("T")
U = TypeVar("U")


class GPT4AllChain(Chain[T, U]):
    """
    GPT4AllChain is a Chain that allows you to run local LLMs easily
    using [GPT4All](https://gpt4all.io/) model.

    [GPT4All](https://gpt4all.io/) is a project that focuses on making
    the LLM models very small and very fast to be able to run in any computer
    without GPUs. Check out more about the project [here](https://gpt4all.io/).

    You can use it as any other chain, on the first use, it will download the model
    (a few GB). Alternatively, you can point to a locally downloaded model.bin file.

    There are serveral parameters you can use to adjust the model output such as
    `temperature`, `max_tokens`, `top_k`, `repeat_penalty`, etc, you can read more
    about them [here](https://docs.gpt4all.io/gpt4all_python.html#generation-parameters).

    Example
    -------

    >>> from litechain import join_final_output
    >>> from litechain.contrib import GPT4AllChain
    >>> import asyncio
    ...
    >>> async def example():
    ...     greet_chain = GPT4AllChain[str, str](
    ...         "GreetingChain",
    ...         lambda name: f"### User: Hello, my name is {name}. How is it going?\\n\\n### Response:",
    ...         model="orca-mini-3b.ggmlv3.q4_0.bin",
    ...         temperature=0,
    ...     )
    ...
    ...     return await join_final_output(greet_chain("Alice"))
    ...
    >>> asyncio.run(example()) # doctest:+ELLIPSIS +SKIP
    Found model file at ...
    " I'm doing well, thank you for asking! How about you?"

    """

    def __init__(
        self: "GPT4AllChain[T, str]",
        name: str,
        call: Callable[
            [T],
            str,
        ],
        model: str,
        temperature: float = 0,
        max_tokens: int = 200,
        top_k=40,
        top_p=0.1,
        repeat_penalty=1.18,
        repeat_last_n=64,
        n_batch=8,
        n_threads: Optional[int] = None,
    ) -> None:
        gpt4all = GPT4All(model, n_threads=n_threads)

        async def generate(prompt: str) -> AsyncGenerator[U, None]:
            loop = asyncio.get_event_loop()

            def get_outputs() -> Iterable[str]:
                return gpt4all.generate(
                    prompt,
                    streaming=True,
                    temp=temperature,
                    max_tokens=max_tokens,
                    top_k=top_k,
                    top_p=top_p,
                    repeat_penalty=repeat_penalty,
                    repeat_last_n=repeat_last_n,
                    n_batch=n_batch,
                )

            outputs = await loop.run_in_executor(None, get_outputs)

            for output in outputs:
                yield cast(U, output)

        super().__init__(name, lambda input: generate(call(input)))
