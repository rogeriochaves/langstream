---
sidebar_position: 3
---

# OpenAI Function Calling

By default, LLMs take text as input, and product text as output, but when we are building LLM applications, many times we want some specific outputs from the LLM, or to fork the execution flow to take the user in another direction. One way to do that, is to ask the LLM to produce a JSON, and the try to parse that JSON. Problem is, often times this JSON can be invalid, and it's a bit hassle to work with it.

So OpenAI developed a feature that constrains the logits to produce a valid structure[[1]](https://github.com/newhouseb/clownfish/), effectively getting them to create a valid schema for doing function calling, which enables us to get structured output and routing effortlessly. You can read more about it in their [official announcement](https://openai.com/blog/function-calling-and-other-api-updates).

To pass a function for [`OpenAIChatChain`](pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatChain) to call, simply pass the function schema in the `function` argument. For example, let's say you want the model to call this function to get the current weather:

```python
from typing import TypedDict, Literal

class WeatherReturn(TypedDict):
    location: str
    forecast: str
    temperature: str

def get_current_weather(
    location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
) -> WeatherReturn:
    return WeatherReturn(
        location=location,
        forecast="sunny",
        temperature="25 C" if format == "celsius" else "77 F",
    )
```

This function simply returns a mocked weather response using the `WeatherReturn` type. Then, to have the model to build the arguments for it, you can pass the function schema like this:

```python
from typing import Union
from litechain import Chain, collect_final_output
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
import json

chain: Chain[str, Union[OpenAIChatDelta, WeatherReturn]] = OpenAIChatChain[
    str, OpenAIChatDelta
](
    "WeatherChain",
    lambda user_input: [
        OpenAIChatMessage(role="user", content=user_input),
    ],
    model="gpt-3.5-turbo",
    functions=[
        {
            "name": "get_current_weather",
            "description": "Gets the current weather in a given location, use this function for any questions related to the weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "description": "The city to get the weather, e.g. San Francisco. Guess the location from user messages",
                        "type": "string",
                    },
                    "format": {
                        "description": "A string with the full content of what the given role said",
                        "type": "string",
                        "enum": ("celsius", "fahrenheit"),
                    },
                },
            },
            "required": ["location"],
        }
    ],
    temperature=0,
).map(
    lambda delta: get_current_weather(**json.loads(delta.content))
    if delta.role == "function" and delta.name == "get_current_weather"
    else delta
)

await collect_final_output(
    chain(
        "I'm in my appartment in Amsterdam, thinking... should I take an umbrella for my pet chicken?"
    )
)
# [{'location': 'Amsterdam', 'forecast': 'sunny', 'temperature': '25 C'}]
```

With the `functions` schema in place, we then map the deltas comming from `OpenAIChatChain`, and from there we call our actual function by decoding the json containing the arguments in case the delta is a function.

Notice how the output type of the chain becomes `Union[OpenAIChatDelta, WeatherReturn]`, this is because the chain now can return either a simple message reply, if the user says "hello, what's up" for example, or it may return a `WeatherReturn` because they user has asked about the weather and therefore we called the function. You could then wire this response to another LLM call to reply the user message for example.

As a tip, if you don't want to write the schema yourself, you can extract it from the function definition, check it out our [example on it](../examples/openai-function-call-extract-schema).

That's it for OpenAI Function Calling, now if want to run an LLM locally, check it out the next guide on GPT4All.

[[1]](https://github.com/newhouseb/clownfish/): Long read if you are interested on how logits constraining work: https://github.com/newhouseb/clownfish/
