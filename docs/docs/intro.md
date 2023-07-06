---
sidebar_position: 1
---

# Getting Started

LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable.

You can install it with pip:

```
pip install litechain
```

## Your First Chain

To run this example, first you will need to get an [API key from OpenAI](https://platform.openai.com), then export it with:

```
export OPENAI_API_KEY=<your key here>
```

(if you really cannot get access to the API, you can try [GPT4All](pathname:///reference/litechain/contrib/index.html#litechain.contrib.GPT4AllChain) instead, it's completely free and runs locally)

Now create a new file `main.py` and paste this example:

```python
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
import asyncio

# Creating a GPT-3.5 EmojiChain
emoji_chain = OpenAIChatChain[str, OpenAIChatDelta](
    "EmojiChain",
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
        async for output in emoji_chain(input()):
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

Continue on reading to learn the Chain basics, we will then build up on more complex examples, can't wait!
