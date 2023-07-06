---
sidebar_position: 3
---

# LLMs

Large Language Models like GPT-4 is the whole reason LiteChain exists, we want to build on top of LLMs to construct an application. After learning the [Chain Basics](/docs/chain-basics), it should be clear how you can wrap any LLM in a [`Chain`](pathname:///reference/litechain/index.html#chain), you just need to produce an [`AsyncGenerator`](https://peps.python.org/pep-0525/) out of their output. However, LiteChain already come with some LLM chains out of the box to make it easier.

Like other things that are not part of the core of the library, they live under `litechain.contrib`. Go ahead for OpenAI examples.