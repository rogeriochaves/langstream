import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, List, Literal, Optional, TypeVar, cast
from colorama import Fore

import openai

from litechain.core.chain import Chain

T = TypeVar("T")
U = TypeVar("U")


class OpenAICompletionChain(Chain[T, U]):
    """
    `OpenAICompletionChain` uses the most simple LLMs from OpenAI based on GPT-3 for text completion, if you are looking for ChatCompletion, take a look at `OpenAIChatChain`.

    The `OpenAICompletionChain` takes a lambda function that should return a string with the prompt for completion.

    To use this chain you will need an `OPENAI_API_KEY` environment variable to be available, and then you can generate completions out of it.

    You can read more about the completion API on [OpenAI API reference](https://platform.openai.com/docs/api-reference/completions)

    Example
    -------

    >>> from litechain import join_final_output
    >>> from litechain.contrib import OpenAICompletionChain
    >>> import asyncio
    ...
    >>> async def example():
    ...     recipe_chain = OpenAICompletionChain[str, str](
    ...         "RecipeChain",
    ...         lambda recipe_name: f"Here is my {recipe_name} recipe: ",
    ...         model="ada",
    ...     )
    ...
    ...     return await join_final_output(recipe_chain("instant noodles"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    '【Instant Noodles】\\n\\nIngredients:\\n\\n1 cup of water'

    """

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
    """
    OpenAIChatMessage is a data class that represents a chat message for building `OpenAIChatChain` prompt.

    Attributes
    ----------
    role : Literal["system", "user", "assistant"]
        The role of who sent this message in the chat, can be one of `"system"`, `"user"` or `"assisant"` (TODO: functions to be supported)

    content : str
        A string with the full content of what the given role said

    """
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class OpenAIChatDelta:
    """
    OpenAIChatDelta is a data class that represents the output of an `OpenAIChatChain`.

    Attributes
    ----------
    role : Optional[Literal["assistant"]]
        The role of the output message, the first message will have the role, while
        the subsequent partial content output ones will have the role as `None`.
        For now the only possible values it will have is either None or `"assistant"` (TODO: functions to be supported)

    content : str
        A string with the partial content being outputted by the LLM, this generally
        translate to each token the LLM is producing

    """
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
    """
    `OpenAIChatChain` gives you access to the more powerful LLMs from OpenAI, like `gpt-3.5-turbo` and `gpt-4`, they are structured in a chat format with roles.

    The `OpenAIChatChain` takes a lambda function that should return a list of `OpenAIChatMessage` for the assistant to reply, it is stateless, so it doesn't keep
    memory of the past chat messages, you will have to handle the memory yourself, you can [follow this guide to get started on memory](https://rogeriochaves.github.io/litechain/docs/llms/memory).

    The `OpenAIChatChain` also produces `OpenAIChatDelta` as output, one per token, it contains the `role` that started the output, and then subsequent `content` updates.
    If you want the final content as a string, you will need to use the `.content` property from the delta and accumulate it for the final result.

    To use this chain you will need an `OPENAI_API_KEY` environment variable to be available, and then you can generate chat completions out of it.

    You can read more about the chat completion API on [OpenAI API reference](https://platform.openai.com/docs/api-reference/chat)

    Example
    -------

    >>> from litechain import Chain, join_final_output
    >>> from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
    >>> import asyncio
    ...
    >>> async def example():
    ...     recipe_chain: Chain[str, str] = OpenAIChatChain[str, OpenAIChatDelta](
    ...         "RecipeChain",
    ...         lambda recipe_name: [
    ...             OpenAIChatMessage(
    ...                 role="system",
    ...                 content="You are ChefGPT, an assistant bot trained on all culinary knowledge of world's most proeminant Michelin Chefs",
    ...             ),
    ...             OpenAIChatMessage(
    ...                 role="user",
    ...                 content=f"Hello, could you write me a recipe for {recipe_name}?",
    ...             ),
    ...         ],
    ...         model="gpt-3.5-turbo",
    ...         max_tokens=10,
    ...     ).map(lambda delta: delta.content)
    ...
    ...     return await join_final_output(recipe_chain("instant noodles"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    "Of course! Here's a simple and delicious recipe"

    """

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
