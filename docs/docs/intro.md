---
sidebar_position: 1
title: Getting Started
---

# Introduction

LangStream is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LangStream focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable, with Streams instead of chains as the building block.

LangStream also puts emphasis on "explicit is better than implicit", which means less magic and a bit more legwork, but on the other hand, you will be able to understand everything that is going on in between, making your application easy to maintain and customize.

## Getting Started

You can install langstream with pip + a model provider (like openai, gpt4all or litellm):

```
pip install langstream openai
```

## Your First Stream

To run this example, first you will need to get an [API key from OpenAI](https://platform.openai.com), then export it with:

```
export OPENAI_API_KEY=<your key here>
```

(if you really cannot get access to the API, you can try [GPT4All](pathname:///reference/langstream/contrib/index.html#langstream.contrib.GPT4AllStream) instead, it's completely free and runs locally)

Now create a new file `main.py` and paste this example:

```python
from langstream.contrib import OpenAIChatStream, OpenAIChatMessage, OpenAIChatDelta
import asyncio

# Creating a GPT-3.5 EmojiStream
emoji_stream = OpenAIChatStream[str, OpenAIChatDelta](
    "EmojiStream",
    lambda user_message: [
        OpenAIChatMessage(
            role="user", content=f"{user_message}. Reply in emojis"
        )
    ],
    model="gpt-3.5-turbo",
    temperature=0,
)

async def main():
    while True:
        print("> ", end="")
        async for output in emoji_stream(input()):
            print(output.data.content, end="")
        print("")

asyncio.run(main())
```

Now run it with

```
python main.py
```

This will create a basic chat on the terminal, and for any questions you ask the bot, it will answer in emojis. If you terminal does not support emojis, try changing the prompt, asking it to reply in ASCII art for example.

## Next Steps

Continue on reading to learn the Stream basics, we will then build up on more complex examples, can't wait!
