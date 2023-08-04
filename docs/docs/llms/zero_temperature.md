---
sidebar_position: 6
---

# Zero Temperature

LLMs work by predicting the next token, the token that gets chosen is the one with the highest probability to be the next one, calculated given the input and all the model training, this is the magic of LLMs in short.

When temperature is zero, it means the LLM will always choose the highest probability tokens, making the output of it more stable, this is great for development, because you have more repeatable results. Setting temperature to zero may also get you more correct output from the LLM, although it may feel a bit more "bland" and less "creative", so it might not be the best end user experience, that's why ChatGPT does not have temperature zero by default, for example.

In a way, it follows the analogy with temperature in physics, when temperature is high, atoms get agitaded and moving all around, when temperature is low, they are more stable and move less, in more predictable manners.

We then recommend setting the temperature of your LLMs to zero for development, to be able to develop and test it with more ease, and once everything is in place, you can try to increase the temperature of some streams and retest to see if the results feel better.