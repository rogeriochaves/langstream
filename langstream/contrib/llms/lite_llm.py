import asyncio
from dataclasses import dataclass
import itertools
from types import GeneratorType
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

import litellm
from colorama import Fore
from retry import retry

from langstream.core.stream import Stream, StreamOutput

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


@dataclass
class LiteLLMChatMessage:
    """
    LiteLLMChatMessage is a data class that represents a chat message for building `LiteLLMChatStream` prompt.

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
class LiteLLMChatDelta:
    """
    LiteLLMChatDelta is a data class that represents the output of an `LiteLLMChatStream`.

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

    def __stream_debug__(self):
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


class LiteLLMChatStream(Stream[T, U]):
    """
    `LiteLLMChatStream` is a wrapper for [LiteLLM](https://github.com/BerriAI/litellm), which gives you access to OpenAI, Azure OpenAI, Anthropic, Google VertexAI,
    HuggingFace, Replicate, A21, Cohere and a bunch other LLMs all the the same time, all while keeping the standard OpenAI chat interface. Check it out the completion API
    and the available models [on their docs](https://docs.litellm.ai/docs/).

    Be aware not all models support streaming, and LangStream by default tries to stream everything. So if the model you choose is not working, you might need to set `stream=False`,
    when calling the `LiteLLMChatStream`

    The `LiteLLMChatStream` takes a lambda function that should return a list of `LiteLLMChatMessage` for the assistant to reply, it is stateless, so it doesn't keep
    memory of the past chat messages, you will have to handle the memory yourself, you can [follow this guide to get started on memory](https://rogeriochaves.github.io/langstream/docs/llms/memory).

    The `LiteLLMChatStream` also produces `LiteLLMChatDelta` as output, one per token, it contains the `role` that started the output, and then subsequent `content` updates.
    If you want the final content as a string, you will need to use the `.content` property from the delta and accumulate it for the final result.

    To use this stream you will need to have the proper environment keys available depending on the model you are using, like `OPENAI_API_KEY`, `COHERE_API_KEY`, `HUGGINGFACE_API_KEY`, etc,
    check it out more details on [LiteLLM docs](https://docs.litellm.ai/docs/completion/supported)

    Example
    -------

    >>> from langstream import Stream, join_final_output
    >>> from langstream.contrib import LiteLLMChatStream, LiteLLMChatMessage, LiteLLMChatDelta
    >>> import asyncio
    ...
    >>> async def example():
    ...     recipe_stream: Stream[str, str] = LiteLLMChatStream[str, LiteLLMChatDelta](
    ...         "RecipeStream",
    ...         lambda recipe_name: [
    ...             LiteLLMChatMessage(
    ...                 role="system",
    ...                 content="You are Chef Claude, an assistant bot trained on all culinary knowledge of world's most proeminant Michelin Chefs",
    ...             ),
    ...             LiteLLMChatMessage(
    ...                 role="user",
    ...                 content=f"Hello, could you write me a recipe for {recipe_name}?",
    ...             ),
    ...         ],
    ...         model="claude-2",
    ...         max_tokens=10,
    ...     ).map(lambda delta: delta.content)
    ...
    ...     return await join_final_output(recipe_stream("instant noodles"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    "Of course! Here's a simple and delicious recipe"

    You can also pass LiteLLM function schemas in the `function` argument with all parameter definitions, just like for OpenAI model, but be aware that not all models support it.
    Once you pass a `function` param, the model may then produce a `function` role `LiteLLMChatDelta` as output,
    using your function, with the `content` field as a json which you can parse to call an actual function.

    Take a look [at our OpenAI guide](https://rogeriochaves.github.io/langstream/docs/llms/open_ai_functions) to learn more about LLM function calls in LangStream, it works the same with LiteLLM.

    Function Call Example
    ---------------------

    >>> from langstream import Stream, collect_final_output
    >>> from langstream.contrib import LiteLLMChatStream, LiteLLMChatMessage, LiteLLMChatDelta
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
    ...     stream : Stream[str, Union[LiteLLMChatDelta, Dict[str, str]]] = LiteLLMChatStream[str, Union[LiteLLMChatDelta, Dict[str, str]]](
    ...         "WeatherStream",
    ...         lambda user_input: [
    ...             LiteLLMChatMessage(role="user", content=user_input),
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
    ...     return await collect_final_output(stream("how is the weather today in Rio de Janeiro?"))
    ...
    >>> asyncio.run(example()) # doctest:+SKIP
    [{'location': 'Rio de Janeiro', 'forecast': 'sunny', 'temperature': '25 C'}]

    """

    def __init__(
        self: "LiteLLMChatStream[T, LiteLLMChatDelta]",
        name: str,
        call: Callable[
            [T],
            List[LiteLLMChatMessage],
        ],
        model: str,
        custom_llm_provider: Optional[str] = None,
        stream: bool = True,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[Literal["none", "auto"], Dict[str, Any]]] = None,
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
        timeout: int = 5,
        retries: int = 3,
    ) -> None:
        async def chat_completion(
            messages: List[LiteLLMChatMessage],
        ) -> AsyncGenerator[StreamOutput[LiteLLMChatDelta], None]:
            loop = asyncio.get_event_loop()

            @retry(tries=retries)
            def get_completions():
                function_kwargs = {}
                if functions is not None:
                    function_kwargs["functions"] = functions
                if function_call is not None:
                    function_kwargs["function_call"] = function_call

                return litellm.completion(
                    request_timeout=timeout,
                    model=model,
                    custom_llm_provider=custom_llm_provider,
                    messages=[m.to_dict() for m in messages],
                    temperature=temperature,  # type: ignore (why is their type int?)
                    stream=stream,
                    max_tokens=max_tokens,  # type: ignore (why is their type float?)
                    **function_kwargs,
                )

            completions = await loop.run_in_executor(None, get_completions)

            pending_function_call: Optional[LiteLLMChatDelta] = None

            completions = (
                completions if isinstance(completions, GeneratorType) else [completions]
            )
            for output in completions:
                output = cast(dict, output)
                if "choices" not in output:
                    continue

                if len(output["choices"]) == 0:
                    continue

                delta = (
                    output["choices"][0]["message"]
                    if "delta" not in output["choices"][0]
                    else output["choices"][0]["delta"]
                )

                if "function_call" in delta:
                    role = delta["role"] if "role" in delta else None
                    function_name: Optional[str] = delta["function_call"].get("name")
                    function_arguments: Optional[str] = delta["function_call"].get(
                        "arguments"
                    )

                    if function_name is not None:
                        pending_function_call = LiteLLMChatDelta(
                            role="function",
                            name=function_name,
                            content=function_arguments or "",
                        )
                    elif (
                        pending_function_call is not None
                        and function_arguments is not None
                    ):
                        pending_function_call.content += function_arguments
                elif "content" in delta:
                    role = delta["role"] if "role" in delta else None
                    yield self._output_wrap(
                        LiteLLMChatDelta(
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
