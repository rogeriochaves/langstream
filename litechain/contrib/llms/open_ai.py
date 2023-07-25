import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
)

import openai
from colorama import Fore
from retry import retry

from litechain.core.chain import Chain, ChainOutput

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


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
        timeout: int = 5,
        retries: int = 3,
    ) -> None:
        async def completion(prompt: str) -> AsyncGenerator[U, None]:
            loop = asyncio.get_event_loop()

            @retry(tries=retries)
            def get_completions():
                return openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    request_timeout=timeout,
                )

            completions = await loop.run_in_executor(None, get_completions)

            for output in completions:
                output = cast(dict, output)
                if "choices" in output:
                    if len(output["choices"]) > 0:
                        if "text" in output["choices"][0]:
                            yield output["choices"][0]["text"]

        super().__init__(name, lambda input: completion(call(input)))


@dataclass
class OpenAIChatMessage:
    """
    OpenAIChatMessage is a data class that represents a chat message for building `OpenAIChatChain` prompt.

    Attributes
    ----------
    role : Literal["system", "user", "assistant", "function"]
        The role of who sent this message in the chat, can be one of `"system"`, `"user"`, `"assistant"` or "function"

    name: Optional[str]
        The name is used for when `role` is `"function"`, it represents the name of the function that was called

    content : str
        A string with the full content of what the given role said

    """

    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class OpenAIChatDelta:
    """
    OpenAIChatDelta is a data class that represents the output of an `OpenAIChatChain`.

    Attributes
    ----------
    role : Optional[Literal["assistant", "function"]]
        The role of the output message, the first message will have the role, while
        the subsequent partial content output ones will have the role as `None`.
        For now the only possible values it will have is either None or `"assistant"`

    name: Optional[str]
        The name is used for when `role` is `"function"`, it represents the name of the function that was called

    content : str
        A string with the partial content being outputted by the LLM, this generally
        translate to each token the LLM is producing

    """

    role: Optional[Literal["assistant", "function"]]
    content: str
    name: Optional[str] = None

    def __chain_debug__(self):
        name = ""
        if self.name:
            name = f" {self.name}"
        if self.role is not None:
            print(f"{Fore.YELLOW}{self.role.capitalize()}{name}:{Fore.RESET} ", end="")
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

    You can also pass OpenAI function schemas in the `function` argument with all parameter definitions, the model may then produce a `function` role `OpenAIChatDelta`,
    using your function, with the `content` field as a json which you can parse to call an actual function.

    Take a look [at our guide](https://rogeriochaves.github.io/litechain/docs/llms/open_ai_functions) to learn more about OpenAI function calls in LiteChain.

    Function Call Example
    ---------------------

    >>> from litechain import Chain, collect_final_output
    >>> from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
    >>> from typing import Literal, Union, Dict
    >>> import asyncio
    ...
    >>> async def example():
    ...     def get_current_weather(
    ...         location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
    ...     ) -> Dict[str, str]:
    ...         return {
    ...             "location": location,
    ...             "forecast": "sunny",
    ...             "temperature": "25 C" if format == "celsius" else "77 F",
    ...         }
    ...
    ...     chain : Chain[str, Union[OpenAIChatDelta, Dict[str, str]]] = OpenAIChatChain[str, Union[OpenAIChatDelta, Dict[str, str]]](
    ...         "WeatherChain",
    ...         lambda user_input: [
    ...             OpenAIChatMessage(role="user", content=user_input),
    ...         ],
    ...         model="gpt-3.5-turbo",
    ...         functions=[
    ...             {
    ...                 "name": "get_current_weather",
    ...                 "description": "Gets the current weather in a given location, use this function for any questions related to the weather",
    ...                 "parameters": {
    ...                     "type": "object",
    ...                     "properties": {
    ...                         "location": {
    ...                             "description": "The city to get the weather, e.g. San Francisco. Guess the location from user messages",
    ...                             "type": "string",
    ...                         },
    ...                         "format": {
    ...                             "description": "A string with the full content of what the given role said",
    ...                             "type": "string",
    ...                             "enum": ("celsius", "fahrenheit"),
    ...                         },
    ...                     },
    ...                     "required": ["location"],
    ...                 },
    ...             }
    ...         ],
    ...         temperature=0,
    ...     ).map(
    ...         lambda delta: get_current_weather(**json.loads(delta.content))
    ...         if delta.role == "function" and delta.name == "get_current_weather"
    ...         else delta
    ...     )
    ...
    ...     return await collect_final_output(chain("how is the weather today in Rio de Janeiro?"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    [{'location': 'Rio de Janeiro', 'forecast': 'sunny', 'temperature': '25 C'}]

    """

    def __init__(
        self: "OpenAIChatChain[T, OpenAIChatDelta]",
        name: str,
        call: Callable[
            [T],
            List[OpenAIChatMessage],
        ],
        model: str,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[Literal["none", "auto"], str]] = None,
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
        timeout: int = 5,
        retries: int = 3,
    ) -> None:
        async def chat_completion(
            messages: List[OpenAIChatMessage],
        ) -> AsyncGenerator[ChainOutput[OpenAIChatDelta], None]:
            loop = asyncio.get_event_loop()

            @retry(tries=retries)
            def get_completions():
                function_kwargs = {}
                if functions is not None:
                    function_kwargs["functions"] = functions
                if function_call is not None:
                    function_kwargs["function_call"] = function_call

                return openai.ChatCompletion.create(
                    timeout=timeout,
                    request_timeout=timeout,
                    model=model,
                    messages=[m.to_dict() for m in messages],
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                    **function_kwargs,
                )

            completions = await loop.run_in_executor(None, get_completions)

            pending_function_call: Optional[OpenAIChatDelta] = None

            for output in completions:
                output = cast(dict, output)
                if "choices" not in output:
                    continue

                if len(output["choices"]) == 0:
                    continue

                if "delta" not in output["choices"][0]:
                    continue

                if "function_call" in output["choices"][0]["delta"]:
                    delta = output["choices"][0]["delta"]
                    role = delta["role"] if "role" in delta else None
                    function_name: Optional[str] = delta["function_call"].get("name")
                    function_arguments: Optional[str] = delta["function_call"].get(
                        "arguments"
                    )

                    if function_name is not None:
                        pending_function_call = OpenAIChatDelta(
                            role="function",
                            name=function_name,
                            content=function_arguments or "",
                        )
                    elif (
                        pending_function_call is not None
                        and function_arguments is not None
                    ):
                        pending_function_call.content += function_arguments
                elif "content" in output["choices"][0]["delta"]:
                    delta = output["choices"][0]["delta"]
                    role = delta["role"] if "role" in delta else None
                    yield self._output_wrap(
                        OpenAIChatDelta(
                            role=role,
                            content=delta["content"],
                        )
                    )
                else:
                    if pending_function_call:
                        yield self._output_wrap(pending_function_call)
                        pending_function_call = None
            if pending_function_call:
                yield self._output_wrap(pending_function_call)
                pending_function_call = None

        super().__init__(
            name,
            lambda input: cast(AsyncGenerator[U, None], chat_completion(call(input))),
        )
