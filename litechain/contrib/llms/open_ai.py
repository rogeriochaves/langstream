import asyncio
from dataclasses import dataclass
import json
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
from litechain.contrib.utils.open_ai_functions import OpenAIFunction, py2gpt

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
class _OpenAIFunctionCall:
    name: str
    arguments: str


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
        if self.role is not None:
            print(f"{Fore.YELLOW}{self.role.capitalize()}:{Fore.RESET} ", end="")
        if self.role == "function":
            arguments = json.loads(self.content)
            stringified_keywords_list = ", ".join(
                [f"{k}={repr(v)}" for k, v in arguments.items()]
            )
            print(
                f"{self.name}({stringified_keywords_list})",
                end="",
                flush=True,
            )
        else:
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

    You can also pass python functions to be called by the model, LiteChain will convert those functions to OpenAI function schema and call it back automatically.
    The functions you pass must have type signatures and doctypes including for the parameters, otherwise you will get a runtime error. The docs are important because
    this is how you tell the model why should it use that function, and what each parameter means, for better results.

    The function you pass may return either a static value or an `AsyncGenerator`, which means you can call other chains from it. Take a look [at our guide](https://rogeriochaves.github.io/litechain/docs/llms/open_ai_functions)
    to learn more about OpenAI function calls in LiteChain.

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
    ...         \"""
    ...         Gets the current weather in a given location, use this function for any questions related to the weather
    ...
    ...         Parameters
    ...         ----------
    ...         location
    ...             The city to get the weather, e.g. San Francisco. Guess the location from user messages
    ...
    ...         format
    ...             A string with the full content of what the given role said
    ...         \"""
    ...
    ...         return {
    ...             "location": location,
    ...             "forecast": "sunny",
    ...             "temperature": "25 C" if format == "celsius" else "77 F",
    ...         }
    ...
    ...     chain = OpenAIChatChain[str, Union[OpenAIChatDelta, Dict[str, str]]](
    ...         "WeatherChain",
    ...         lambda user_input: [
    ...             OpenAIChatMessage(role="user", content=user_input),
    ...         ],
    ...         model="gpt-3.5-turbo",
    ...         functions=[get_current_weather],
    ...         temperature=0,
    ...     )
    ...
    ...     return await collect_final_output(chain("how is the weather today in Rio de Janeiro?"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    [{'location': 'Rio de Janeiro', 'forecast': 'sunny', 'temperature': '25 C'}]

    """

    def __init__(
        self: "OpenAIChatChain[T, Union[OpenAIChatDelta, V]]",
        name: str,
        call: Callable[
            [T],
            List[OpenAIChatMessage],
        ],
        model: str,
        functions: Union[
            Optional[List[Callable[..., AsyncGenerator[ChainOutput[V, Any], Any]]]],
            Optional[List[Callable[..., AsyncGenerator[V, Any]]]],
            Optional[List[Callable[..., V]]],
        ] = cast(List[Callable[..., OpenAIChatDelta]], None),
        function_call: Optional[Union[Literal["none", "auto"], str]] = None,
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.name = name
        name_to_function, openai_functions = self._parse_functions(functions)

        async def chat_completion(
            messages: List[OpenAIChatMessage],
        ) -> AsyncGenerator[ChainOutput[Union[OpenAIChatDelta, V], Any], Any]:
            loop = asyncio.get_event_loop()

            def get_completions():
                function_kwargs = {}
                if functions is not None:
                    function_kwargs["functions"] = openai_functions
                if function_call is not None:
                    function_kwargs["function_call"] = function_call

                return openai.ChatCompletion.create(
                    model=model,
                    messages=[m.to_dict() for m in messages],
                    temperature=temperature,
                    stream=True,
                    max_tokens=max_tokens,
                    **function_kwargs,
                )

            completions = await loop.run_in_executor(None, get_completions)

            pending_function_calls: List[_OpenAIFunctionCall] = []

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
                        pending_function_calls = [
                            _OpenAIFunctionCall(
                                name=function_name,
                                arguments=function_arguments or "",
                            )
                        ]
                    elif (
                        len(pending_function_calls) > 0
                        and function_arguments is not None
                    ):
                        pending_function_calls[-1].arguments += function_arguments
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
                    async for value in self._run_pending_function_call(
                        name_to_function, pending_function_calls
                    ):
                        yield value
            async for value in self._run_pending_function_call(
                name_to_function, pending_function_calls
            ):
                yield value

        self._call = lambda input: chat_completion(call(input))

    def _parse_functions(self, functions: Optional[List[Callable]]):
        name_to_function: Dict[str, Callable] = dict()
        openai_functions: List[OpenAIFunction] = []
        if functions is not None:
            for fn in functions:
                try:
                    openai_functions = [py2gpt(fn) for fn in functions]
                except ValueError as e:
                    raise ValueError(
                        f"The function {fn} that you passed in the 'functions' argument when creating a OpenAIChatChain could not be converted to a valid OpenAI function: {str(e)}"
                    )
            name_to_function = dict(
                [
                    (openai_fn["name"], fn)
                    for fn, openai_fn in zip(functions, openai_functions)
                ]
            )

        return name_to_function, openai_functions

    async def _run_pending_function_call(
        self,
        name_to_function: Dict[str, Callable],
        pending_function_calls: List[_OpenAIFunctionCall],
    ) -> AsyncGenerator[ChainOutput, None]:
        for function_call in pending_function_calls:
            function_to_call = name_to_function[function_call.name]
            arguments = json.loads(function_call.arguments)
            output_chain_name = f"{self.name}@function_call->{function_call.name}"

            yield self._output_wrap(
                OpenAIChatDelta(
                    role="function",
                    name=function_call.name,
                    content=function_call.arguments,
                ),
                final=False,
            )

            result = function_to_call(**arguments)
            wrapped = self._wrap(result, name=output_chain_name)
            async for output in wrapped:
                yield output
        pending_function_calls.clear()
