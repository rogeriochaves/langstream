"""
The Contrib module is where all the other chains and integrations that build on top of
core Chain module live. Here you can import the LLMs you want to use.

>>> from litechain.contrib import OpenAIChatChain, GPT4AllChain # etc

---

Here you can find the reference and code examples, for further tutorials and use cases, consult the [documentation](https://github.com/rogeriochaves/litechain).
"""

from litechain.contrib.llms.open_ai import (
    OpenAICompletionChain,
    OpenAIChatChain,
    OpenAIChatMessage,
    OpenAIChatDelta,
)
from litechain.contrib.llms.gpt4all_chain import GPT4AllChain

__all__ = (
    "OpenAICompletionChain",
    "OpenAIChatChain",
    "OpenAIChatMessage",
    "OpenAIChatDelta",
    "GPT4AllChain",
)
