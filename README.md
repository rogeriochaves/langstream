# 🪽🔗 LiteChain

[![](https://dcbadge.vercel.app/api/server/AmEMWmFG?style=flat)](https://discord.gg/AmEMWmFG)
[![Release Notes](https://img.shields.io/github/release/rogeriochaves/litechain)](https://pypi.org/project/litechain/)
[![tests](https://github.com/rogeriochaves/litechain/actions/workflows/run_tests.yml/badge.svg)](https://github.com/rogeriochaves/litechain/actions/workflows/run_tests.yml)
[![docs](https://github.com/rogeriochaves/litechain/actions/workflows/publish_docs.yml/badge.svg)](https://github.com/rogeriochaves/litechain/actions/workflows/publish_docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/rogeriochaves/litechain/blob/main/LICENSE)

LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable.

[Documentation](https://rogeriochaves.github.io/litechain)

# Quick Install

```
pip install litechain
```

# 🔗 The Chain building block

The Chain is the building block for LiteChain, an LLM is a Chain, an output parser is a Chain, a group of chains can be composed as another Chain, it's [Chains all the way down](https://en.wikipedia.org/wiki/Turtles_all_the_way_down).

Take a look at [the documentation](https://rogeriochaves.github.io/litechain) for guides on building on chains and building LLM applications, or go straight to [the reference](https://rogeriochaves.github.io/litechain/reference/litechain/index.html#chain) for the core concept and modules available.

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

In this simple example, we are creating a [GPT4 Chain](https://rogeriochaves.github.io/litechain/reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatChain) that takes the user message and appends `". Reply in emojis"` to it for building the prompt, following the [OpenAI chat structure](https://rogeriochaves.github.io/litechain/reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatMessage) and with [zero temperature](https://rogeriochaves.github.io/litechain/docs/llms/zero_temperature).

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

As you can see, it's easy enough to connect two Chains together using the `and_then` function. There are other functions available for composition such as `map`, `collect`, `join` and `gather`, they form the small set of abstractions you need to learn to build complex Chain compositions for your application, and they behave as you would expect if you have Function Programming knowledge. You can read all about it in the [reference](https://rogeriochaves.github.io/litechain/reference/litechain/index.html). Once you learn those functions, any Chain will follow the same patterns, enabling you to build complex LLM applications.

As you may also have noticed, Chains accept type signatures, EmojiChain has the type `[str, OpenAIChatDelta]`, while TranslatorChain has the type `[Iterable[OpenAIChatDelta], OpenAIChatDelta]`, those mean respectively the *input* and *output* types of each Chain. Since the EmojiChain is taking user output, it simply takes a `str` as input, and since it's using OpenAI Chat API with GPT-4, it produces `OpenAIChatDelta`, which is [the tokens that GPT-4 produces one at a time](https://rogeriochaves.github.io/litechain/reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatDelta). TranslatorChain then takes `Iterable[OpenAIChatDelta]` as input, since it's connected with the output from EmojiChain, it takes the full list of the generated tokens to later extract their content and form its own prompt.

The type signatures are an important part of LiteChain, having them can save a lot of time preventing bugs and debugging issues caused for example when Chain B is not expecting the output of Chain A. Using an editor like VSCode with PyLance allows you to get warned that Chain A doesn't fit into Chain B before you even try to run the code, you can read about LiteChain typing [here](https://rogeriochaves.github.io/litechain/docs/chain-basics/type_signatures).

Last but not least, you may also have noticed that both the emojis and the translation got printed in the final output, this is by design. In LiteChain, you always have access to everything that has gone through the whole chain in the final stream, this means that debugging it is very trivial, and a [`debug`](https://rogeriochaves.github.io/litechain/reference/litechain/index.html#litechain.debug) function is available to make it even easier. A property `output.final : bool` [is available](https://rogeriochaves.github.io/litechain/reference/litechain/index.html#litechain.ChainOutput.final) to be checked if you want to print just the results of the final Chain, but there are also more utility functions available to help you work with output stream as you wish, check out more about it on our [Why Streams? guide](https://rogeriochaves.github.io/litechain/docs/chain-basics/why_streams) and [the reference](https://rogeriochaves.github.io/litechain/reference/litechain/index.html).

# Prompts on the outside

In our experience, when working with LLM applications, the main part you must spend tunning are your prompts, which are not always portable if you switch LLMs. The content one chain produces might change a lot how another chain should be written, the prompt carry the personality and the goal of your app, doing good prompt engineering can really make it or break it.

That's why LiteChain does not hide prompts away in agents, we will give examples in the documentation, but believe you should build your own agents, to be able to customize them and their prompts later. LiteChain simply wants to facilitate and standardize the piping and connection between different parts, so you can focus on what is really important, we don't want you to spend time with LiteChain itself.

# Bring your own integration

In addition, as the name implies, LiteChain wants to stay light, not embrace the world, the goal is that you really understand the Chain, making it very easy for your to add your own integration, without any additional layers in between.

In our experience, wrappers can hurt more than they help, because instead of using the library or API you want to connect directly, now you need to learn another layer of indirection, which might not accept the same parameters to work the way you expect, it gets in the way.

We do provide some integrations for OpenAI and GPT4All for example, but then we try to have a very thin layer, and to stay as close as possible to the original API, to the point that you can use the oficial documentation for it.

# 📖 Learn more

To continue developing with LiteChain, take a look at our [documentation](https://rogeriochaves.github.io/litechain) so you can find:

- Getting started
- Detailed guides
- How-to examples
- Reference

# 👥 Community

[Join our discord](https://discord.gg/AmEMWmFG) community to connect with other LiteChain developers, ask questions, get support, and stay updated with the latest news and announcements.

[![Join our Discord community](https://img.shields.io/badge/Join-Discord-7289DA.svg)](https://discord.gg/AmEMWmFG)

# 🚙 Roadmap

- [ ] Add an example for document retrieval using vector search
- [ ] Add a `filter` function
- [ ] Add docs for debugging
- [ ] Add default error handling
- [ ] Add a simple default memory mechanism

# 🙋 Contributing

As a very new project in a rapidly developing field LiteChain is extremely open to contributions, we need a lot of help with integrations, documentation and guides content, feel free to send MRs and open issues. The project is very easy to run (check out the Makefile, it's all you need), but more complete contibuting guidelines to be written (we need help with that too!)

If you want to help me pay the bills and keep developing this project, you can:

<a href="https://www.buymeacoffee.com/rchaves" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>