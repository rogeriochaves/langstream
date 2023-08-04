# 🪽🔗 LangStream

> ⚠️ Heads up! LiteChain was renamed to LangStream, for more details, check out [issue #4](https://github.com/rogeriochaves/langstream/issues/4)

[![](https://dcbadge.vercel.app/api/server/48ZM5KkKgw?style=flat)](https://discord.gg/48ZM5KkKgw)
[![Release Notes](https://img.shields.io/github/release/rogeriochaves/langstream)](https://pypi.org/project/langstream/)
[![tests](https://github.com/rogeriochaves/langstream/actions/workflows/run_tests.yml/badge.svg)](https://github.com/rogeriochaves/langstream/actions/workflows/run_tests.yml)
[![docs](https://github.com/rogeriochaves/langstream/actions/workflows/publish_docs.yml/badge.svg)](https://github.com/rogeriochaves/langstream/actions/workflows/publish_docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/rogeriochaves/langstream/blob/main/LICENSE)

LangStream is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LangStream focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable, with Streams instead of chains as the building block.

[Documentation](https://rogeriochaves.github.io/langstream)

# Quick Install

```
pip install langstream
```

# 🔗 The Stream building block

The Stream is the building block for LangStream, an LLM is a Stream, an output parser is a Stream, a group of streams can be composed as another Stream, it's [Streams all the way down](https://en.wikipedia.org/wiki/Turtles_all_the_way_down).

Take a look at [the documentation](https://rogeriochaves.github.io/langstream) for guides on building on streams and building LLM applications, or go straight to [the reference](https://rogeriochaves.github.io/langstream/reference/langstream/index.html#stream) for the core concept and modules available.

# Quick Example

Here is a ChatBot that answers anything you ask using only emojis:

```python
from langstream.contrib import OpenAIChatStream, OpenAIChatMessage, OpenAIChatDelta
from typing import Iterable

# Creating a GPT-4 EmojiStream
emoji_stream = OpenAIChatStream[str, OpenAIChatDelta](
    "EmojiStream",
    lambda user_message: [
        OpenAIChatMessage(
            role="user", content=f"{user_message}. Reply in emojis"
        )
    ],
    model="gpt-4",
    temperature=0,
)

# Now interacting with it
async for output in emoji_stream("Hey there, how is it going?"):
    print(output.data.content, end="")

#=> 👋😊👍💻🌞

async for output in emoji_stream("What is answer to the ultimate question of life, the universe, and everything?"):
    print(output.data.content, end="")

#=> 4️⃣2️⃣
```

In this simple example, we are creating a [GPT4 Stream](https://rogeriochaves.github.io/langstream/reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatStream) that takes the user message and appends `". Reply in emojis"` to it for building the prompt, following the [OpenAI chat structure](https://rogeriochaves.github.io/langstream/reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatMessage) and with [zero temperature](https://rogeriochaves.github.io/langstream/docs/llms/zero_temperature).

Then, as you can see, we have an async loop going over each token output from `emoji_stream`. In LangStream, everything is an async stream using Python's `AsyncGenerator` class, and the most powerful part of it, is that you can connect those streams by composing two Streams together:

```python
# Creating another Stream to translate back from emoji
translator_stream = OpenAIChatStream[Iterable[OpenAIChatDelta], OpenAIChatDelta](
    "TranslatorStream",
    lambda emoji_tokens: [
        OpenAIChatMessage(
            role="user", content=f"Translate this emoji message {[token.content for token in emoji_tokens]} to plain english"
        )
    ],
    model="gpt-4",
)

# Connecting the two Streams together
stream = emoji_stream.and_then(translator_stream)

# Trying out the whole flow
async for output in stream("Hey there, how is it going?"):
    print(output.data.content, end="")

#=> 👋😊👍💻🌞"Hello, have a nice day working on your computer!"
```

As you can see, it's easy enough to connect two Streams together using the `and_then` function. There are other functions available for composition such as `map`, `collect`, `join` and `gather`, they form the small set of abstractions you need to learn to build complex Stream compositions for your application, and they behave as you would expect if you have Function Programming knowledge. You can read all about it in the [reference](https://rogeriochaves.github.io/langstream/reference/langstream/index.html). Once you learn those functions, any Stream will follow the same patterns, enabling you to build complex LLM applications.

As you may also have noticed, Streams accept type signatures, EmojiStream has the type `[str, OpenAIChatDelta]`, while TranslatorStream has the type `[Iterable[OpenAIChatDelta], OpenAIChatDelta]`, those mean respectively the *input* and *output* types of each Stream. Since the EmojiStream is taking user output, it simply takes a `str` as input, and since it's using OpenAI Chat API with GPT-4, it produces `OpenAIChatDelta`, which is [the tokens that GPT-4 produces one at a time](https://rogeriochaves.github.io/langstream/reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatDelta). TranslatorStream then takes `Iterable[OpenAIChatDelta]` as input, since it's connected with the output from EmojiStream, it takes the full list of the generated tokens to later extract their content and form its own prompt.

The type signatures are an important part of LangStream, having them can save a lot of time preventing bugs and debugging issues caused for example when Stream B is not expecting the output of Stream A. Using an editor like VSCode with PyLance allows you to get warned that Stream A doesn't fit into Stream B before you even try to run the code, you can read about LangStream typing [here](https://rogeriochaves.github.io/langstream/docs/stream-basics/type_signatures).

Last but not least, you may also have noticed that both the emojis and the translation got printed in the final output, this is by design. In LangStream, you always have access to everything that has gone through the whole stream in the final stream, this means that debugging it is very trivial, and a [`debug`](https://rogeriochaves.github.io/langstream/reference/langstream/index.html#langstream.debug) function is available to make it even easier. A property `output.final : bool` [is available](https://rogeriochaves.github.io/langstream/reference/langstream/index.html#langstream.StreamOutput.final) to be checked if you want to print just the results of the final Stream, but there are also more utility functions available to help you work with output stream as you wish, check out more about it on our [Why Streams? guide](https://rogeriochaves.github.io/langstream/docs/stream-basics/why_streams) and [the reference](https://rogeriochaves.github.io/langstream/reference/langstream/index.html).

# Prompts on the outside

In our experience, when working with LLM applications, the main part you must spend tunning are your prompts, which are not always portable if you switch LLMs. The content one stream produces might change a lot how another stream should be written, the prompt carry the personality and the goal of your app, doing good prompt engineering can really make it or break it.

That's why LangStream does not hide prompts away in agents, we will give examples in the documentation, but believe you should build your own agents, to be able to customize them and their prompts later. LangStream simply wants to facilitate and standardize the piping and connection between different parts, so you can focus on what is really important, we don't want you to spend time with LangStream itself.

# Bring your own integration

In addition, as the name implies, LangStream wants to stay light, not embrace the world, the goal is that you really understand the Stream, making it very easy for your to add your own integration, without any additional layers in between.

In our experience, wrappers can hurt more than they help, because instead of using the library or API you want to connect directly, now you need to learn another layer of indirection, which might not accept the same parameters to work the way you expect, it gets in the way.

We do provide some integrations for OpenAI and GPT4All for example, but then we try to have a very thin layer, and to stay as close as possible to the original API, to the point that you can use the oficial documentation for it.

# 📖 Learn more

To continue developing with LangStream, take a look at our [documentation](https://rogeriochaves.github.io/langstream) so you can find:

- Getting started
- Detailed guides
- How-to examples
- Reference

# 👥 Community

[Join our discord](https://discord.gg/48ZM5KkKgw) community to connect with other LangStream developers, ask questions, get support, and stay updated with the latest news and announcements.

[![Join our Discord community](https://img.shields.io/badge/Join-Discord-7289DA.svg)](https://discord.gg/AmEMWmFG)

# 🚙 Roadmap

- [ ] Add docs for debugging
- [ ] Add a simple default memory mechanism
- [ ] Consider RxPY as the underlying stream handler
- [ ] Add a compat adapter to reuse LangChain tools with LangStream

# 🙋 Contributing

As a very new project in a rapidly developing field LangStream is extremely open to contributions, we need a lot of help with integrations, documentation and guides content, feel free to send MRs and open issues. The project is very easy to run (check out the Makefile, it's all you need), but more complete contibuting guidelines to be written (we need help with that too!)

If you want to help me pay the bills and keep developing this project, you can:

<a href="https://www.buymeacoffee.com/rchaves" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>