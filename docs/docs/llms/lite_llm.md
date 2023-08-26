---
sidebar_position: 5
---

# Lite LLM (Azure, Anthropic, etc)

[Lite LLM](https://github.com/BerriAI/litellm) is a library that wraps the API of many other LLMs APIs such as Azure, Anthropic, Cohere, HuggingFace, Replicate, and so on, standardizing all of them to use the same API surface as OpenAI Chat Completion API. LangStream provides a wrapper to LiteLLM so you can build your streams on most of the LLMs available on the market. To check all possible models, take a look at [Lite LLM Docs](https://docs.litellm.ai/docs/completion/supported).

To use the multiple LLMs provided by Lite LLM, you will need to have in your environment the API keys depending on which model you are going to use of course, for example:

```
export OPENAI_API_KEY=<your key here>
export AZURE_API_BASE=<your key here>
export ANTHROPIC_API_KEY=<your key here>
export HUGGINGFACE_API_KEY=<your key here>
```

Then, you should be able to use the [`LiteLLMChatStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.LiteLLMChatStream), which has basically the same interface as as the [`OpenAIChatStream`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatStream), check it out:

## Chat Completion

```python
from langstream import Stream, join_final_output
from langstream.contrib import LiteLLMChatStream, LiteLLMChatMessage, LiteLLMChatDelta

recipe_stream: Stream[str, str] = LiteLLMChatStream[str, LiteLLMChatDelta](
    "RecipeStream",
    lambda recipe_name: [
        LiteLLMChatMessage(
            role="system",
            content="You are ChefLiteLLM, an assistant bot trained on all culinary knowledge of world's most proeminant Michelin Chefs",
        ),
        LiteLLMChatMessage(
            role="user",
            content=f"Hello, could you write me a recipe for {recipe_name}?",
        ),
    ],
    model="gpt-3.5-turbo",
).map(lambda delta: delta.content)

await join_final_output(recipe_stream("instant noodles"))
#=> "Of course! Here's a simple and delicious recipe for instant noodles:\n\nIngredients:\n- 1 packet of instant noodles (your choice of flavor)\n- 2 cups of water\n- 1 tablespoon of vegetable oil\n- 1 small onion, thinly sliced\n- 1 clove of garlic, minced\n- 1 small carrot, julienned\n- 1/2 cup of sliced mushrooms\n- 1/2 cup of shredded cabbage\n- 2 tablespoons of soy sauce\n- 1 teaspoon of sesame oil\n- Optional toppings: sliced green onions, boiled egg, cooked chicken or shrimp, chili flakes\n\nInstructions:\n1. In a medium-sized pot, bring the water to a boil. Add the instant noodles and cook according to the package instructions until they are al dente. Drain and set aside.\n\n2. In the same pot, heat the vegetable oil over medium heat. Add the sliced onion and minced garlic, and sauté until they become fragrant and slightly caramelized.\n\n3. Add the julienned carrot, sliced mushrooms, and shredded cabbage to the pot. Stir-fry for a few minutes until the vegetables are slightly softened.\n\n4. Add the cooked instant noodles to the pot and toss them with the vegetables.\n\n5. In a small bowl, mix together the soy sauce and sesame oil. Pour this mixture over the noodles and vegetables, and toss everything together until well combined.\n\n6. Cook for an additional 2-3 minutes, stirring occasionally, to allow the flavors to meld together.\n\n7. Remove the pot from heat and divide the noodles into serving bowls. Top with your desired toppings such as sliced green onions, boiled egg, cooked chicken or shrimp, and chili flakes.\n\n8. Serve the instant noodles hot and enjoy!\n\nFeel free to customize this recipe by adding your favorite vegetables or protein. Enjoy your homemade instant noodles!"
```

Analogous to OpenAI, it takes [`LiteLLMChatMessage`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.LiteLLMChatMessage)s and produces [`LiteLLMChatDelta`](pathname:///reference/langstream/contrib/index.html#langstream.contrib.LiteLLMChatDelta)s, it can also take `functions` as an argument for function calling, but keep in mind not all models support it and it might simply be ignored, be sure to check [Lite LLM Docs](https://docs.litellm.ai/docs/completion/supported) for the model you are using.

Another caveat is that, by default, LangStream tries to stream all outputs, but not all models and APIs support streaming, so you might need to disable it with `stream=False` or they might throw exceptions, again be sure to check which models support it or not.

We hope that with that you will be able to use the best LLM available to you, or even mix and match on the middle of your streams depending on the need, or falling back if one LLM is not generating the right answer, and so on.

Keep on reading the next part of the docs!