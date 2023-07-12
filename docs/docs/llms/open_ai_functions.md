---
sidebar_position: 3
---

# OpenAI Function Calling

By default, LLMs take text as input, and product text as output, but when we are building LLM applications, many times we want some specific outputs from the LLM, or to fork the execution flow to take the user in another direction. One way to do that, is to ask the LLM to produce a JSON, and the try to parse that JSON. Problem is, often times this JSON can be invalid, and it's a bit hassle to work with it.

So OpenAI developed a feature that constrains the logits to produce a valid structure[[1]](https://github.com/newhouseb/clownfish/), effectively getting them to create a valid schema for doing function calling, which enables us to get structured output and routing effortlessly. You can read more about it in their [official announcement](https://openai.com/blog/function-calling-and-other-api-updates).

LiteChain then integrates OpenAI functions even more deeply, allowing you to pass actual Python functions and call other chains from it.

To pass a function for [`OpenAIChatChain`](pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatChain) to call, first you will have to declare it with parameter [types](https://docs.python.org/3/library/typing.html) and [docstrings](https://www.programiz.com/python-programming/docstrings), those are essential for the model to know when should it call this function, what is the type it should produce for each parameter, and what each parameter is about. Writing it well is like writing your prompts well, because that's what the model will be reading, if something is missing, you will get a runtime error.

Declare your function like this:

```python
from typing import TypedDict, Literal

class WeatherReturn(TypedDict):
    location: str
    forecast: str
    temperature: str

def get_current_weather(
    location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
) -> WeatherReturn:
    """
    Gets the current weather in a given location, use this function for any questions related to the weather

    Parameters
    ----------
    location
        The city to get the weather, e.g. San Francisco. Guess the location from user messages

    format
        A string with the full content of what the given role said
    """

    return WeatherReturn(
        location=location,
        forecast="sunny",
        temperature="25 C" if format == "celsius" else "77 F",
    )
```

Notice how we are using `Literal["celsius", "fahrenheit"]` in the `format` parameter, this works as an enum, and limits the values that the model can inject there. Notice also the full docstring, documenting what the function does and why it should be called, and each of the parameters. You don't need to repeat the parameter types on the docstring because they are already defined on the function signature.

Finally, we create the `WeatherReturn` for ourselves to organize the output, but the return type will not really be considered by the model.

Now that you have a proper documented function, you can simply pass it to [`OpenAIChatChain`](pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatChain), and it will be smart enough to know when to use it:

```python
from typing import Union
from litechain import collect_final_output
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta

chain = OpenAIChatChain[str, Union[OpenAIChatDelta, WeatherReturn]](
    "WeatherChain",
    lambda user_input: [
        OpenAIChatMessage(role="user", content=user_input),
    ],
    model="gpt-3.5-turbo",
    functions=[get_current_weather],
    temperature=0,
)

await collect_final_output(
    chain(
        "I'm in my appartment in Amsterdam, thinking... should I take an umbrella for my pet chicken?"
    )
)
# [{'location': 'Amsterdam', 'forecast': 'sunny', 'temperature': '25 C'}]
```

Notice how the output type of the chain is `Union[OpenAIChatDelta, WeatherReturn]`, this is because the chain now can return either a simple message reply, if the user says "hello, what's up" for example, or it may return a `WeatherReturn` because they user has asked about the weather and therefore called the function. The return types get wired up automatically by the type system so you get no surprises of what things you are possibly getting back from the chain.

Now, to go one step beyond, not necessarily you function has to return simple values, you can also call other chains from it, so effectively one LLM is calling the other! 🤯 Check out this example:

```python
from typing import TypedDict, Literal, Union
from litechain import debug, collect_final_output
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
import json

class WeatherReturn(TypedDict):
    location: str
    forecast: str
    temperature: str

def chain(user_input: str):
    def reply_with_current_weather(
        location: str, format: Literal["celsius", "fahrenheit"] = "celsius"
    ):
        """
        Gets the current weather in a given location and replies user, use this function for any questions related to the weather"

        Parameters
        ----------
        location
            The city to get the weather, e.g. San Francisco. Guess the location from user messages

        format
            A string with the full content of what the given role said
        """

        weather: WeatherReturn = {
            "location": location,
            "forecast": "sunny",
            "temperature": "25 C" if format == "celsius" else "77 F",
        }

        return weather_reply_chain(weather)

    weather_chain = OpenAIChatChain[str, OpenAIChatDelta](
        "WeatherChain",
        lambda user_input: [
            OpenAIChatMessage(role="user", content=user_input),
        ],
        model="gpt-3.5-turbo",
        functions=[reply_with_current_weather],
        temperature=0,
    )

    weather_reply_chain = OpenAIChatChain[WeatherReturn, OpenAIChatDelta](
        "WeatherReplyChain",
        lambda weather: [
            OpenAIChatMessage(role="user", content=user_input),
            OpenAIChatMessage(
                role="user",
                content=f"Output from the weather system: {json.dumps(weather)}",
            ),
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )

    return debug(weather_chain)(user_input)

await collect_final_output(
    chain(
        "I'm in my appartment in Amsterdam, thinking... should I take an umbrella for my pet chicken?"
    )
)
# > WeatherChain
#
# Function: reply_with_current_weather(location='Amsterdam')
#
# > WeatherReplyChain
#
# Assistant: Based on the current weather forecast in Amsterdam, it is sunny with a temperature of 25°C. Since it is not raining, you do not need to take an umbrella for your pet chicken. Enjoy the sunny weather!
```

Here we used the [`debug`](pathname:///reference/litechain/utils/chain.html#litechain.utils.chain.debug) function to show what is going on, you can see it first called the function, and then it gave a proper reply about the Amsterdam weather.

The way it works is that we create a function `chain`, which takes the `user_input`, creates the `reply_with_current_weather` function and two chains, the `weather_chain` and the `weather_reply_chain`. The first chain just take the user input and find the appropriate function to call, the function `reply_with_current_weather` then actually fetches the weather and call the second chain `weather_reply_chain`, which reuses the `user_input` plus takes the `WeatherReturn` as input and generate the final reply.

That's it for OpenAI Function Calling, now if want to run an LLM locally, check it out the next guide on GPT4All.

[[1]](https://github.com/newhouseb/clownfish/): Long read if you are interested on how logits constraining work: https://github.com/newhouseb/clownfish/
