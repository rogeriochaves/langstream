import asyncio
from typing import AsyncGenerator, Callable, Optional, TypeVar, cast

from litechain.core.chain import Chain
from litechain.utils.async_generator import as_async_generator
import openai


T = TypeVar("T")
U = TypeVar("U")


class OpenAICompletionChain(Chain[T, U]):
    def __init__(
        self: "OpenAICompletionChain[T, str]",
        name: str,
        call: Callable[
            [T],
            str,
        ],
        model: str,
        temperature=0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.name = name

        async def completion(prompt) -> AsyncGenerator[str, None]:
            loop = asyncio.get_event_loop()

            def get_completions():
                return openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                )

            completions = await loop.run_in_executor(None, get_completions)

            for output in completions:
                output = cast(dict, output)
                if "choices" in output:
                    if len(output["choices"]) > 0:
                        if "text" in output["choices"][0]:
                            yield output["choices"][0]["text"]

        self._call = lambda input: completion(call(input))
