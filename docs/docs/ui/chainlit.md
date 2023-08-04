---
sidebar_position: 1
---

# Chainlit Integration

[Chainlit](https://github.com/Chainlit/chainlit) is a UI that gives you a ChatGPT like interface for your streams, it is very easy to set up, it has a slick UI, and it allows you to visualize the intermediary steps, so it's great for development!

You can install it with:

```
pip install chainlit
```

Then since we have access to all intermediary steps in LangStream, integrating it with Chainlit is as easy as this:

```python
from typing import Dict
import chainlit as cl

@cl.on_message
async def on_message(message: str):
    messages_map: Dict[str, cl.Message] = {}

    async for output in stream(message):
        if output.stream in messages_map:
            cl_message = messages_map[output.stream]
            await cl_message.stream_token(output.data.content)
        else:
            messages_map[output.stream] = cl.Message(
                author=output.stream,
                content=output.data.content,
                indent=0 if output.final else 1,
            )
            await messages_map[output.stream].send()
```

Here we are calling our stream, which is an [`OpenAIChatStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatStream), creating a new message as soon as a stream outputs, and streaming it new content as it arrives. We also `indent` the message to mark it as an intermediary step if the output is not `final`.

Using our emoji translator example from before, this is how it is going to look like:

<video src="/langstream/img/chainlit-demo.mp4" width="100%" controls style={{padding: "8px 0 32px 0"}}></video>

Here is the complete code for an integration example:

```python title="main.py"
from typing import Dict, Iterable, List, Tuple, TypedDict

import chainlit as cl

from langstream import debug
from langstream.contrib import OpenAIChatStream, OpenAIChatDelta, OpenAIChatMessage


class Memory(TypedDict):
    history: List[OpenAIChatMessage]


memory = Memory(history=[])


def save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:
    memory["history"].append(message)
    return message


def update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:
    if memory["history"][-1].role != delta.role and delta.role is not None:
        memory["history"].append(
            OpenAIChatMessage(role=delta.role, content=delta.content)
        )
    else:
        memory["history"][-1].content += delta.content
    return delta


translator_stream = OpenAIChatStream[Iterable[OpenAIChatDelta], OpenAIChatDelta](
    "TranslatorStream",
    lambda emoji_tokens: [
        OpenAIChatMessage(
            role="user",
            content=f"Translate this emoji message {[token.content for token in emoji_tokens]} to plain english",
        )
    ],
    model="gpt-4",
)

stream = (
    debug(
        OpenAIChatStream[str, OpenAIChatDelta](
            "EmojiChatStream",
            lambda user_message: [
                *memory["history"],
                save_message_to_memory(
                    OpenAIChatMessage(
                        role="user", content=f"{user_message}. Reply in emojis"
                    )
                ),
            ],
            model="gpt-3.5-turbo-0613",
            temperature=0,
        )
    )
    .map(update_delta_on_memory)
    .and_then(debug(translator_stream))
)

@cl.on_message
async def on_message(message: str):
    messages_map: Dict[str, Tuple[bool, cl.Message]] = {}

    async for output in stream(message):
        if "@" in output.stream and not output.final:
            continue
        if output.stream in messages_map:
            sent, cl_message = messages_map[output.stream]
            if not sent:
                await cl_message.send()
                messages_map[output.stream] = (True, cl_message)
            await cl_message.stream_token(output.data.content)
        else:
            messages_map[output.stream] = (
                False,
                cl.Message(
                    author=output.stream,
                    content=output.data.content,
                    indent=0 if output.final else 1,
                ),
            )
```

You can run it with:

```
chainlit run main.py -w
```