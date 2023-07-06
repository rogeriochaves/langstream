"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[53],{1109:e=>{e.exports=JSON.parse('{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"tutorialSidebar":[{"type":"link","label":"Getting Started","href":"/litechain/docs/intro","docId":"intro"},{"type":"category","label":"Chain Basics","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Why Streams?","href":"/litechain/docs/chain-basics/why_streams","docId":"chain-basics/why_streams"},{"type":"link","label":"Working with Streams","href":"/litechain/docs/chain-basics/working_with_streams","docId":"chain-basics/working_with_streams"},{"type":"link","label":"Composing Chains","href":"/litechain/docs/chain-basics/composing_chains","docId":"chain-basics/composing_chains"},{"type":"link","label":"Type Signatures","href":"/litechain/docs/chain-basics/type_signatures","docId":"chain-basics/type_signatures"}],"href":"/litechain/docs/chain-basics/"},{"type":"category","label":"LLMs","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"OpenAI LLMs","href":"/litechain/docs/llms/open_ai","docId":"llms/open_ai"},{"type":"link","label":"GPT4All LLMs","href":"/litechain/docs/llms/gpt4all","docId":"llms/gpt4all"},{"type":"link","label":"Zero Temperature","href":"/litechain/docs/llms/zero_temperature","docId":"llms/zero_temperature"}],"href":"/litechain/docs/llms/"},{"type":"html","value":"<a class=\'menu__link\' style=\'margin-top: 2px\' href=\'/litechain/reference/litechain/index.html\'>API Reference \ud83d\udcd6</a>"}]},"docs":{"chain-basics/composing_chains":{"id":"chain-basics/composing_chains","title":"Composing Chains","description":"If you are familiar with Functional Programming, the Chain follows the Monad Laws, this ensures they are composable to build complex application following the Category Theory definitions. Our goal on building LiteChain was always to make it truly composable, and this is the best abstraction we know for the job, so we adopted it.","sidebar":"tutorialSidebar"},"chain-basics/index":{"id":"chain-basics/index","title":"Chain Basics","description":"The Chain is the main building block of LiteChain, you compose chains together to build your LLM application.","sidebar":"tutorialSidebar"},"chain-basics/type_signatures":{"id":"chain-basics/type_signatures","title":"Type Signatures","description":"In the recent years, Python has been expanding the support for type hints, which helps a lot during development to catch bugs from types that should not be there, and even detecting Nones before they happen.","sidebar":"tutorialSidebar"},"chain-basics/why_streams":{"id":"chain-basics/why_streams","title":"Why Streams?","description":"For a visualization on streaming vs blocking, take a look at vercel docs on AI streaming, they have a nice animation there","sidebar":"tutorialSidebar"},"chain-basics/working_with_streams":{"id":"chain-basics/working_with_streams","title":"Working with Streams","description":"By default, all LLMs generate a stream of tokens:","sidebar":"tutorialSidebar"},"intro":{"id":"intro","title":"Getting Started","description":"LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable.","sidebar":"tutorialSidebar"},"llms/gpt4all":{"id":"llms/gpt4all","title":"GPT4All LLMs","description":"LLMs require a lot of GPU to run properly make it hard for the common folk to set one up locally. Fortunately, the folks at GPT4All are doing an excellent job in really reducing those models with various techniques, and speeding them up to run on CPUs everywhere with no issues. LiteChain also provides a thin wrapper for them, and since it\'s local, no API keys are required.","sidebar":"tutorialSidebar"},"llms/index":{"id":"llms/index","title":"LLMs","description":"Large Language Models like GPT-4 is the whole reason LiteChain exists, we want to build on top of LLMs to construct an application. After learning the Chain Basics, it should be clear how you can wrap any LLM in a Chain, you just need to produce an AsyncGenerator out of their output. However, LiteChain already come with some LLM chains out of the box to make it easier.","sidebar":"tutorialSidebar"},"llms/open_ai":{"id":"llms/open_ai","title":"OpenAI LLMs","description":"OpenAI took the world by storm with the launch of ChatGPT and GPT-4, at the point of this writing, they are still the smartest LLMs out there. To use them, first you will need to get an API key from OpenAI, and export it with:","sidebar":"tutorialSidebar"},"llms/zero_temperature":{"id":"llms/zero_temperature","title":"Zero Temperature","description":"LLMs work by predicting the next token, the token that gets chosen is the one with the highest probability to be the next one, calculated given the input and all the model training, this is the magic of LLMs in short.","sidebar":"tutorialSidebar"}}}')}}]);