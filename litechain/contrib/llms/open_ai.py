import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, List, Literal, Optional, TypeVar, cast
from colorama import Fore

import openai

from litechain.core.chain import Chain

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
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.name = name

        async def completion(prompt: str) -> AsyncGenerator[str, None]:
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


@dataclass
class OpenAIChatMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class OpenAIChatDelta:
    role: Optional[Literal["assistant"]]
    content: str

    def __chain_debug__(self):
        if self.role is not None:
            print(f"{Fore.YELLOW}{self.role.capitalize()}:{Fore.RESET} ", end="")
        print(
            self.content,
            end="",
            flush=True,
        )


class OpenAIChatChain(Chain[T, U]):
    def __init__(
        self: "OpenAIChatChain[T, OpenAIChatDelta]",
        name: str,
        call: Callable[
            [T],
            List[OpenAIChatMessage],
        ],
        model: str,
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.name = name

        async def chat_completion(
            messages: List[OpenAIChatMessage],
        ) -> AsyncGenerator[OpenAIChatDelta, None]:
            loop = asyncio.get_event_loop()

            def get_completions():
                return openai.ChatCompletion.create(
                    model=model,
                    messages=[m.__dict__ for m in messages],
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                )

            completions = await loop.run_in_executor(None, get_completions)

            for output in completions:
                output = cast(dict, output)
                if "choices" in output:
                    if len(output["choices"]) > 0:
                        if "delta" in output["choices"][0]:
                            if "content" in output["choices"][0]["delta"]:
                                delta = output["choices"][0]["delta"]
                                role = delta["role"] if "role" in delta else None
                                yield OpenAIChatDelta(
                                    role=role, content=delta["content"]
                                )

        self._call = lambda input: chat_completion(call(input))
