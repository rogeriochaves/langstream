---
sidebar_position: 3
---

# LLMs

Large Language Models like GPT-4 is the whole reason LangStream exists, we want to build on top of LLMs to construct an application. After learning the [Stream Basics](/docs/stream-basics), it should be clear how you can wrap any LLM in a [`Stream`](pathname:///reference/langstream/index.html#stream), you just need to produce an [`AsyncGenerator`](https://peps.python.org/pep-0525/) out of their output. However, LangStream already come with some LLM streams out of the box to make it easier.

Like other things that are not part of the core of the library, they live under `langstream.contrib`. Go ahead for OpenAI examples.