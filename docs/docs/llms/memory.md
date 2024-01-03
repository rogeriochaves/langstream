---
sidebar_position: 6
---

# Adding Memory

LLMs are stateless, and LangStream also strive to be as stateless as possible, which makes things easier to reason about. However, this means your Streams will have no memory by default.

Following the "explicit is better than implicit" philosophy, in LangStream you manage the memory yourself, so you are in full control of what is stored to memory and where it is used and when.

## Simple Text Completion Memory

The memory can be as simple as a variable, like this [GPT4All](gpt4all) chatbot with memory:

```python
from langstream import Stream, join_final_output
from langstream.contrib import GPT4AllStream
from textwrap import dedent

memory = ""

def save_to_memory(str: str) -> str:
    global memory
    memory += str
    return str

magical_numbers_bot: Stream[str, str] = GPT4AllStream[str, str](
    "MagicalNumbersStream",
    lambda user_message:
        memory
        + save_to_memory(f"""\n
            ### User: {user_message}

            ### Response:"""
        ),
    model="orca-mini-3b-gguf2-q4_0.gguf",
    temperature=0,
).map(save_to_memory)

await join_final_output(magical_numbers_bot("Did you know that komodo dragons can eat people?"))
#=> 'Yes, I do know that fact. They are known to be one of the largest and deadliest lizards in the world.'

await join_final_output(magical_numbers_bot("Would you like to be one?"))
#=> ' As an AI, I am not capable of feeling emotions or desires to eat people.'
```

In the second question, `"Would you like to be one?"`, there is no mention of komodo dragons or eating people, still, the LLM was able to answer it considering previous context, this proves that memory is working properly.

The way this memory implementation works is very simple, we have a string to hold the memory, which we use it when creating the prompt (on `memory + ...`).

Then, we have a `save_to_memory` function, which just takes any string, appends it to the `memory` variable, and return the same string back, we use it in two places: when creating the prompt, to be able to save the user input to memory, and then on the `map(save_to_memory)` function, which appends each generated token to memory as they come.

Try adding some `print(memory)` statements before and after each stream call to see how memory is changing.

## OpenAI Chat Memory

Adding memory to OpenAI Chat is a bit more tricky, because it takes a list of [`OpenAIChatMessage`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatMessage)s for the prompt, and generates [`OpenAIChatDelta`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatMessage)s as output.

This means that we cannot use a simple string as memory, but we can use a simple list. Also now we need a function to update the last message on the memory with the incoming delta for each update, like this:

```python
from langstream import Stream, join_final_output
from langstream.contrib import OpenAIChatMessage, OpenAIChatDelta, OpenAIChatStream
from typing import List


memory: List[OpenAIChatMessage] = []


def save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:
    memory.append(message)
    return message


def update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:
    if memory[-1].role != delta.role and delta.role is not None:
        memory.append(OpenAIChatMessage(role=delta.role, content=delta.content))
    else:
        memory[-1].content += delta.content
    return delta


stream: Stream[str, str] = (
    OpenAIChatStream[str, OpenAIChatDelta](
        "EmojiChatStream",
        lambda user_message: [
            *memory,
            save_message_to_memory(
                OpenAIChatMessage(
                    role="user", content=f"{user_message}. Reply in emojis"
                )
            ),
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    .map(update_delta_on_memory)
    .map(lambda delta: delta.content)
)

await join_final_output(stream("Hey there, my name is 🧨 how is it going?"))
#=> '👋🧨😊'

await join_final_output(stream("What is my name?"))
#=> '🤔❓🧨'
```

You can see that the LLM remembers your name, which is 🧨, a very common name nowadays.

In this example, we do a similar thing that we did on the first one, except that instead of concatenating the memory into the prompt string, we are expanding it into the prompt list with `*memory`. Also, we cannot use the same function on the `map` call, because we don't have full messages back, but deltas, which we need to use to update the last message on the memory, the function `update_delta_on_memory` takes care of that for us.

I hope this guide now made it more clear how can you have memory on your Streams. In future releases, LangStream might release a more standard way of dealing with memory, but this is not the case yet, please join us in the discussion on how an official memory module should look like if you have ideas!