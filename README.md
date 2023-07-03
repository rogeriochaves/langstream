# 🪽🔗 LiteChain

LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable.

# Quick Install

```
pip install git+https://github.com/rogeriochaves/litechain.git#egg=litechain
```

# Quick Example

Here is a ChatBot that answers anything you ask using only emojis:

```python
from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta
from typing import Iterable

# Creating a GPT-4 EmojiChain
emoji_chain = OpenAIChatChain[str, OpenAIChatDelta](
    "EmojiChain",
    lambda user_message: [
        OpenAIChatMessage(
            role="user", content=f"{user_message}. Reply in emojis"
        )
    ],
    model="gpt-4",
    temperature=0,
)

# Now interacting with it
async for output in emoji_chain("Hey there, how is it going?"):
    print(output.data.content, end="")

#=> 👋😊👍💻🌞

async for output in emoji_chain("What is answer to the ultimate question of life, the universe, and everything?"):
    print(output.data.content, end="")

#=> 4️⃣2️⃣
```

In this simple example, we are creating a [GPT4 Chain](#) (TODO: link pending) that takes the user message and appends `". Reply in emojis"` to it for building the prompt, following the [OpenAI chat structure](#) (TODO: link pending) and with [zero temperature](#) (TODO: link pending).

Then, as you can see, we have an async loop going over each token output from `emoji_chain`. In LiteChain, everything is an async stream using Python's `AsyncGenerator` class, and the most powerful part of it, is that you can connect those streams by composing two Chains together:

```python
# Creating another Chain to translate back from emoji
translator_chain = OpenAIChatChain[Iterable[OpenAIChatDelta], OpenAIChatDelta](
    "TranslatorChain",
    lambda emoji_tokens: [
        OpenAIChatMessage(
            role="user", content=f"Translate this emoji message {[token.content for token in emoji_tokens]} to plain english"
        )
    ],
    model="gpt-4",
)

# Connecting the two Chains together
chain = emoji_chain.and_then(translator_chain)

# Trying out the whole flow
async for output in chain("Hey there, how is it going?"):
    print(output.data.content, end="")

#=> 👋😊👍💻🌞"Hello, have a nice day working on your computer!"
```

As you can see, it's easy enough to connect two Chains together using the `and_then` function. There are other functions available for composition such as `map`, `collect`, `join` and `gather`, they form the small set of abstractions you need to learn to build complex Chain compositions for your application, and they behave as you would expect if you have Function Programming knowledge. You can read all about it in the [reference](#) (TODO: link pending). Once you learn those functions, any Chain will follow the same patterns, enabling you to build complex LLM applications.

As you may also have noticed, Chains accept type signatures, EmojiChain has the type `[str, OpenAIChatDelta]`, while TranslatorChain has the type `[Iterable[OpenAIChatDelta], OpenAIChatDelta]`, those mean respectively the *input* and *output* types of each Chain. Since the EmojiChain is taking user output, it simply takes a `str` as input, and since it's using OpenAI Chat API with GPT-4, it produces `OpenAIChatDelta`, which is [the tokens that GPT-4 produces one at a time](#) (TODO: link pending). TranslatorChain then takes `Iterable[OpenAIChatDelta]` as input, since it's connected with the output from EmojiChain, it takes the full list of the generated tokens to later extract their content and form its own prompt.

The type signatures are an important part of LiteChain, having them can save a lot of time preventing bugs and debugging issues caused for example when Chain B is not expecting the output of Chain A. Using an editor like VSCode with PyLance allows you to get warned that Chain A doesn't fit into Chain B before you even try to run the code. (TODO: add a types guide)

Last but not least, you may also have noticed that both the emojis and the translation got printed in the final output, this is by design. In LiteChain, you always have access to everything that has gone through the whole chain in the final stream, this means that debugging it is very trivial, and a [`debug`](#) (TODO: link pending) function is available to make it even easier. A property `output.final : bool` is available to be checked if you want to print just the results of the final Chain, but there are also more utility functions available to help you work with output stream as you wish, check them out on [the reference](#) (TODO: link pending).

# The Chain building block

# Development

Install all dependencies:

```
pip install -r requirements.txt
```

Run all the tests:

```
python -m unittest tests/**/*.py
python -m doctest -v litechain/**/*.py
```
