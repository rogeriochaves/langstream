---
sidebar_position: 2
---

# Why Streams?

:::tip My tip

For a visualization on streaming vs blocking, take a look at [vercel docs](https://sdk.vercel.ai/docs/concepts/streaming) on AI streaming, they have a nice animation there

:::

LLMs, at least on their current form, produce tokens one at a time, in a recurrent manner. For a big text, waiting for all tokens to arrive can take quite some time, so it is a better
user experience and dev experience if we can visualize the tokens as they are generated.

Granted, it is not always that we will need or even want the results to be streamed, for example, if you want to use the LLM to generate 3 answers, one as if it were Einsten, one as if it were
Newton, and one as it if were Kanye West, and then generate the answer basing on the arguments of those three for a better result, then of course you need to wait for them to finish first before answering the user. It is, however,
very easy to block a stream and wait for it to finish before moving on, but the other way around, taking a blocking operation, and making a stream out of it, is simply not possible.

That's why streaming is not just a feature for LangStream, it is fundamentally ingrained into the [`Stream`](pathname:///reference/langstream/index.html#stream), under the hood everything is a Python [`AsyncGenerator`](https://peps.python.org/pep-0525/),
the Stream just give us a nice composable and debuggable interface on top.

Continue on reading for examples on how that looks like, and how do we work with those streams.