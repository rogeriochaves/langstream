---
sidebar_position: 5
---

# Type Signatures

In the recent years, Python has been expanding the support for [type hints](https://docs.python.org/3/library/typing.html), which helps a lot during development to catch bugs from types that should not be there, and even detecting `None`s before they happen.

On quick scripts, notebooks, some web apps and throwaway code types might not be very useful and actually get in the way, however, when you are doing a lot of data piping and connecting many different pieces together, types are extremely useful, to help you save time and patience in debugging why two things are not working well together, and this is exactly what LangStream is about.

Because of that, LangStream has a very thorough type annotation, with the goal of making it very reliable for the developer, but it works best when you explicitly declare the input and output types you expect when defining a stream:

```python
len_stream = Stream[str, int]("LenStream", lambda input: len(input))
```

This stream above for example, just counts the length of a string, so it takes a `str` and return an `int`. The nice side-effect of this is that you can see, at a glance, what goes in and what goes out of the stream, without needing to read it's implementation

Now, Let's say you have this other stream:

```python
happy_stream = Stream[str, str]("HappyStream", lambda input: input + " :)")
```

If you try to fit the two, it won't work, but instead of knowing that only when you run the code, you can find out instantly, if you use a code editor like VS Code (with PyLance extension for python type checking), it will look like this:

![vscode showing typecheck error](/img/type-error-1.png)

It says that `"Iterable[int]" is incompatible with "str"`, right, the first stream produces `int`s, so let's transform them to string by adding a `.map(str)`:

![vscode showing typecheck error](/img/type-error-2.png)

It still doesn't typecheck, but now it says that `"Iterable[str]" is incompatible with "str"`, of course, because streams produce a stream of things, not just one thing, and the `happy_stream` expect a single string, so this type error reminded us that we need to use `join()` first:

![vscode showing no type errors](/img/type-error-3.png)

Solved, no type errors now, with instant feedback.

You don't necessarily need to add the types of your streams in LangStream, it can be inferenced from the lambda or function you pass, however, be aware it may end up being not what you want, for example:

```python
first_item_stream = Stream("FirstItemStream", lambda input: input[0])

await collect_final_output(first_item_stream([1, 2, 3]))
#=> [1]

await collect_final_output(first_item_stream("Foo Bar"))
#=> ["F"]
```

The first `first_item_stream` was intended to take the first item only from lists, but it also works with strings actually, since `[0]` works on strings. This might not be what you expected at first, and lead to annoying bugs. If, however, you are explicit about your types, then the second call will show a type error, helping you to notice this early on, maybe before you run it:

```python
first_item_stream = Stream[List[int], int]("FirstItemStream", lambda input: input[0])

await collect_final_output(first_item_stream([1, 2, 3]))
#=> [1]

# highlight-next-line
await collect_final_output(first_item_stream("Foo Bar")) # ❌ type error
#=> ["F"]
```

Now types cannot prevent all errors, some will still happen at runtime. Go to the next page to check out on error handling.