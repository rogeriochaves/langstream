---
sidebar_position: 4
---

# GPT4All LLMs

LLMs require a lot of GPU to run properly make it hard for the common folk to set one up locally. Fortunately, the folks at [GPT4All](https://gpt4all.io/index.html) are doing an excellent job in really reducing those models with various techniques, and speeding them up to run on CPUs everywhere with no issues. LangStream also provides a thin wrapper for them, and since it's local, no API keys are required.

Make sure you have GPT4All installed:

```
pip install gpt4all
```

# GPT4AllStream

You can use a [`GPT4AllStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.GPT4AllStream) like this:

```python
from langstream import join_final_output
from langstream.contrib import GPT4AllStream

greet_stream = GPT4AllStream[str, str](
    "GreetingStream",
    lambda name: f"### User: Hello little person that lives in my CPU, my name is {name}. How is it going?\\n\\n### Response:",
    model="orca-mini-3b.ggmlv3.q4_0.bin",
    temperature=0,
)

await join_final_output(greet_stream("Alice"))
#=> " I'm doing well, thank you for asking! How about you?"
```

The first time you run it, it will download the model you are using (in this case `orca-mini-3b.ggmlv3.q4_0.bin`), you can also specify a pathname there if you wish, you can check out all GPT4All available models [on their website](https://gpt4all.io/index.html) on Model Explorer.

Then, you might have noticed the prompt is just a string, but we do have roles markers inside it, with `### User:` and `### Response:`, with two `\n\n` line breaks in between. This is how GPT4All models were trained, and you can use this same patterns to keep the roles behaviour.

Also, in the example we used `temperature=0`, for stability as explained [here](/docs/llms/zero_temperature), but [`GPT4AllStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.GPT4AllStream) has many more parameters you can adjust that can work better depending on the model you are choosing, check them out on [the reference](pathname:///reference/langstream/contrib/index.html#langstream.contrib.GPT4AllStream).