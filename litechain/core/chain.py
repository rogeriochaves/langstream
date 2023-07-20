"""
Core Chain module
"""
import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from litechain.utils.async_generator import as_async_generator

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
X = TypeVar("X")


@dataclass
class ChainOutput(Generic[T]):
    """
    ChainOutput is a data class that represents the output of a Chain at each step.

    Attributes
    ----------
    chain : str
        The name of the chain that produced this output. This helps in identifying
        which part of the processing pipeline the output is coming from.

    output : Union[T, Any]
        The actual output data produced by the chain. This will be type T for final chain output,
        but can be also be of any type produced by any step of the whole chain.

    final : bool
        A boolean flag indicating whether this output is the final output of the chain.
        Only the outputs at the end of the chain are marked as "final".

    Example
    -------

    >>> from litechain import Chain
    >>> import asyncio
    ...
    >>> async def example():
    ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
    ...     polite_chain = greet_chain.map(lambda greeting: f"{greeting} How are you?")
    ...
    ...     async for output in polite_chain("Alice"):
    ...         # Output is of type ChainOutput
    ...         print(output)
    ...
    >>> asyncio.run(example())
    ChainOutput(chain='GreetingChain', data='Hello, Alice!', final=False)
    ChainOutput(chain='GreetingChain@map', data='Hello, Alice! How are you?', final=True)
    """

    chain: str
    data: Union[T, Any]
    final: bool


class Chain(Generic[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[ChainOutput[U], Any], AsyncGenerator[U, Any], U]
    ]

    def __init__(
        self,
        name: str,
        call: Callable[
            [T],
            Union[AsyncGenerator[ChainOutput[U], Any], AsyncGenerator[U, Any], U],
        ],
    ) -> None:
        self.name = name
        self._call = call

    def __call__(self, input: T) -> AsyncGenerator[ChainOutput[U], Any]:
        result = self._call(input)
        return self._wrap(result)

    def _wrap(
        self,
        value: Union[AsyncGenerator[ChainOutput[V], Any], AsyncGenerator[V, Any], V],
        name: Optional[str] = None,
    ) -> AsyncGenerator[ChainOutput[V], Any]:
        async def _wrap(
            values: Union[AsyncGenerator[ChainOutput[V], Any], AsyncGenerator[V, Any]],
        ) -> AsyncGenerator[ChainOutput[V], Any]:
            async for value in values:
                yield self._output_wrap(value, name=name)

        if isinstance(value, AsyncGenerator):
            return _wrap(value)
        return _wrap(as_async_generator(value))

    def _output_wrap(
        self, value: Union[ChainOutput[V], V], final=None, name=None
    ) -> ChainOutput[V]:
        if isinstance(value, ChainOutput):
            final = final if final is not None else value.final
            return ChainOutput[V](chain=value.chain, data=value.data, final=final)

        final = final if final is not None else True
        return ChainOutput[V](
            chain=self.name if name is None else name, data=value, final=final
        )

    async def _reyield(
        self, async_iterable: AsyncGenerator[ChainOutput[U], Any]
    ) -> AsyncGenerator[Tuple[List[U], ChainOutput[U]], Any]:
        values: List[U] = []
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                values.append(u.data)
            yield (values, u_rewrapped)

    def map(self, fn: Callable[[U], V]) -> "Chain[T, V]":
        """
        Maps the output of the current chain through a function as they arrive.

        The transform function will receive the current output of the chain and
        should return a modified version of it. This method is non-blocking and
        will continue processing the chain in parallel.

        Example:

        >>> from litechain import Chain, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     greet_chain = Chain[str, str]("GreetingChain", lambda name: f"Hello, {name}!")
        ...     polite_chain = greet_chain.map(lambda greeting: f"{greeting} How are you?")
        ...     return await join_final_output(polite_chain("Alice"))
        ...
        >>> asyncio.run(example())
        'Hello, Alice! How are you?'


        Example of processing one token at a time:

        >>> from litechain import Chain, as_async_generator, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_chain = Chain[str, str]("WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))) # produces one word at a time
        ...     accronym_chain = words_chain.map(lambda word: word.upper()[0]) # uppercases each word and take the first letter
        ...     return await join_final_output(accronym_chain("as soon as possible"))
        ...
        >>> asyncio.run(example())
        'ASAP'
        """

        next_name = f"{self.name}@map"

        async def map(input: T) -> AsyncGenerator[ChainOutput[V], Any]:
            # Reyield previous chain so we never block the stream, and at the same time yield mapped values
            prev_len_values = 0
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[V], to_reyield)
                if len(values) > prev_len_values:  # as soon as there is a new value
                    prev_len_values = len(values)
                    yield self._output_wrap(fn(values[-1]), name=next_name)

        return Chain[T, V](next_name, lambda input: map(input))

    def and_then(
        self,
        next: Callable[
            [Iterable[U]],
            Union[AsyncGenerator[ChainOutput[V], Any], AsyncGenerator[V, Any], V],
        ],
    ) -> "Chain[T, V]":
        """
        Processes the output of the current chain through a transformation function or another chain.

        Unlike the map method, which applies transformations to outputs as they arrive,
        the and_then method first collects all the outputs and then passes them to the transformation function or the next chain.
        This method is blocking and will wait for the entire chain to be processed before applying the transformation.

        If `transform` is a function, it should accept the list of collected outputs and return a modified version of it.
        If `transform` is another chain, it is used to process the list of collected outputs.

        Example using a function:

        >>> from litechain import Chain, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     word_chain = Chain[str, str]("WordChain", lambda word: as_async_generator(word, "!"))
        ...     count_chain : Chain[str, int] = word_chain.and_then(lambda outputs: len(list(outputs)))
        ...     return await collect_final_output(count_chain("Hi"))
        ...
        >>> asyncio.run(example())
        [2]


        Example using another chain:

        >>> from litechain import Chain, as_async_generator, join_final_output
        >>> from typing import Iterable
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_chain = Chain[str, str]("WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))) # produces one word at a time
        ...     acronym_chain = Chain[Iterable[str], str]("AcronymChain", lambda words: "".join(word.upper()[0] for word in words)) # produces acronym
        ...     composed_chain = words_chain.and_then(acronym_chain)
        ...     return await join_final_output(composed_chain("as soon as possible"))
        ...
        >>> asyncio.run(example())
        'ASAP'
        """

        next_name = f"{self.name}@and_then"
        if hasattr(next, "name"):
            next_name = next.name

        async def and_then(
            input: T,
        ) -> AsyncGenerator[ChainOutput[V], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[V], to_reyield)
                iter_u = values

            # Then, call in the next chain
            iter_v = self._wrap(next(iter_u), name=next_name)
            async for v in iter_v:
                yield v

        return Chain[T, V](next_name, and_then)

    def collect(self: "Chain[T, U]") -> "SingleOutputChain[T, List[U]]":
        """
        Collects all the outputs produced by the chain and returns them as a list.

        This method is blocking useful when the next chain or processing step needs to have access to the
        entire output all at once, rather than processing elements as they arrive.

        Example:

        >>> from litechain import Chain, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     word_chain: Chain[str, List[str]] = Chain[str, str](
        ...         "WordChain", lambda word: as_async_generator(word, "!")
        ...     ).collect()
        ...     return await collect_final_output(word_chain("Hi"))
        ...
        >>> asyncio.run(example())
        [['Hi', '!']]
        """

        next_name = f"{self.name}@collect"

        async def _collect(
            input: T,
        ) -> AsyncGenerator[ChainOutput[List[U]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[List[U]], to_reyield)
                iter_u = values

            # Then, yield the collected results
            yield self._output_wrap(iter_u, name=next_name)

        return SingleOutputChain[T, List[U]](next_name, _collect)

    def join(self: "Chain[T, str]", separator="") -> "SingleOutputChain[T, str]":
        """
        Joins the output of a string-producing chain into a single string.

        The `join` method concatenates each item in the output of the chain, using the
        provided separator between each element. This is particularly useful when working
        with text, and you want to merge all the generated tokens.

        Note that this method blocks until all outputs of the chain are available, as it
        needs to wait for the complete output to perform the join operation.

        Params
        ----------
        separator : str
            A string that will be used as a separator between the elements. Default is an empty string.

        Example:

        >>> from litechain import Chain, as_async_generator, join_final_output
        >>> import asyncio
        ...
        >>> async def example():
        ...     words_chain = Chain[str, str]("WordsChain", lambda sentence: as_async_generator(*sentence.split(" ")))
        ...     capitalized_chain = words_chain.map(lambda word: word.capitalize())
        ...     joined_chain = capitalized_chain.join(" ")
        ...     return await join_final_output(joined_chain("this is an example"))
        ...
        >>> asyncio.run(example())
        'This Is An Example'
        """

        next_name = f"{self.name}@join"

        async def _join(
            input: T,
        ) -> AsyncGenerator[ChainOutput[str], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[str] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[str], to_reyield)
                iter_u = values

            # Then, return the joined result
            output: str = separator.join(iter_u)
            yield self._output_wrap(output, name=next_name)

        return SingleOutputChain[T, str](next_name, _join)

    def gather(
        self: "Union[Chain[T, AsyncGenerator[ChainOutput[V], Any]], Chain[T, AsyncGenerator[V, Any]]]",
    ) -> "SingleOutputChain[T, List[List[V]]]":
        """
        Gathers results from multiple chains and processes them in parallel.

        The `gather` method is used to process several chains concurrently, and it waits until all of
        them are complete before continuing. This is similar to `asyncio.gather`, and is useful when you
        want to run multiple asynchronous tasks in parallel and wait for all of them to complete.

        Note that the order of results corresponds to the order of chains passed to the `gather` method.

        >>> from litechain import Chain, as_async_generator, collect_final_output
        >>> import asyncio
        ...
        >>> async def delayed_output(x):
        ...     await asyncio.sleep(0.1)
        ...     yield f"Number: {x}"
        ...
        >>> async def example():
        ...     number_chain = Chain[int, int](
        ...         "NumberChain", lambda x: as_async_generator(*range(x))
        ...     )
        ...     gathered_chain : Chain[int, str] = (
        ...         number_chain.map(delayed_output)
        ...         .gather()
        ...         .and_then(lambda results: as_async_generator(*(r[0] for r in results)))
        ...     )
        ...     return await collect_final_output(gathered_chain(3))
        ...
        >>> asyncio.run(example()) # will take 0.1s to finish, not 0.3s, because it runs in parallel
        ['Number: 0', 'Number: 1', 'Number: 2']
        """
        return self.collect().gather()

    def on_error(
        self,
        handler: Callable[[Exception], Union[AsyncGenerator[ChainOutput[V], Any], V]],
    ) -> "Chain[T, Union[U, V]]":
        """
        Handles any uncaught exceptions that might occur during the execution of the current chain.

        The `handler` function takes an exception as its argument and returns a new value that
        will be used as the output of the chain instead of the exception. The function can also re-raise
        the exception or raise a new one, which will then be propagated further up the chain.

        If an exception occurs in the `handler` function itself, it will be propagated without any
        further handling.

        Example:

        >>> from litechain import Chain, join_final_output
        >>> import asyncio
        ...
        >>> def failed_greeting(name: str):
        ...     raise Exception(f"Giving {name} a cold shoulder")
        ...
        >>> async def example():
        ...     greet_chain = Chain[str, str](
        ...         "GreetingChain",
        ...         failed_greeting
        ...     ).on_error(lambda e: f"Sorry, an error occurred: {str(e)}")
        ...
        ...     async for output in greet_chain("Alice"):
        ...         print(output)
        ...
        >>> asyncio.run(example())
        ChainOutput(chain='GreetingChain', data=Exception('Giving Alice a cold shoulder'), final=False)
        ChainOutput(chain='GreetingChain@on_error', data='Sorry, an error occurred: ...', final=True)
        """

        next_name = f"{self.name}@on_error"
        if hasattr(next, "name"):
            next_name = next.name

        async def on_error(
            input: T,
        ) -> AsyncGenerator[ChainOutput[Union[U, V]], Any]:
            try:
                async for output in self(input):
                    yield cast(ChainOutput[Union[U, V]], output)
            except Exception as e:
                yield cast(ChainOutput[Union[U, V]], self._output_wrap(e, final=False))
                async for output in self._wrap(handler(e), name=next_name):
                    yield cast(ChainOutput[Union[U, V]], output)

        return Chain[T, Union[U, V]](next_name, lambda input: on_error(input))


class SingleOutputChain(Chain[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[ChainOutput[U], Any], AsyncGenerator[U, Any], U]
    ]

    async def _reyield(
        self, async_iterable: AsyncGenerator[ChainOutput[U], Any], at: str
    ) -> AsyncGenerator[Tuple[Optional[U], ChainOutput[U]], Any]:
        final_value: Optional[U] = None
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                if final_value is not None:
                    # TODO: try to make this happen with a bad use case, is it even breakable?
                    raise Exception(
                        f"Expected a single item at the end of SingleOutputChain, found multiple for {self.name}@{at}"
                    )
                final_value = u.data
            yield (final_value, u_rewrapped)

    def map(self, fn: Callable[[U], V]) -> "SingleOutputChain[T, V]":
        """
        Similar to `Chain.map`, this method applies a function to the final output of the chain, but returns a SingleOutputChain.

        The `fn` parameter is a function that takes a value of type U and returns a value of type V.

        For detailed examples, refer to the documentation of `Chain.map`.
        """

        next_name = f"{self.name}@map"

        async def map(input: T) -> AsyncGenerator[ChainOutput[V], Any]:
            # Reyield previous chain so we never block the stream, and at the same time yield mapped values
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input), "map"):
                yield cast(ChainOutput[V], to_reyield)
                final_u = value

            if final_u is None:
                # TODO: try to make this happen with a bad use case, is it even breakable?
                raise Exception(
                    f"Expected item at the end of the chain, found None for {self.name}@map"
                )
            yield self._output_wrap(fn(final_u), name=next_name)

        return SingleOutputChain[T, V](next_name, lambda input: map(input))

    def and_then(
        self,
        next: Callable[
            [U],
            Union[AsyncGenerator[ChainOutput[V], Any], AsyncGenerator[V, Any], V],
        ],
    ) -> "Chain[T, V]":
        """
        Similar to `Chain.and_then`, this method takes a function that receives the final output of this chain as its input and returns a new Chain.

        For detailed examples, refer to the documentation of `Chain.and_then`.
        """
        next_name = f"{self.name}@and_then"
        if hasattr(next, "name"):
            next_name = next.name

        async def and_then(
            input: T,
        ) -> AsyncGenerator[ChainOutput[V], Any]:
            # First, reyield previous chain so we never block the stream, and collect the last result when it is done
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input), "and_then"):
                yield cast(ChainOutput[V], to_reyield)
                final_u = value

            if final_u is None:
                # TODO: try to make this happen with a bad use case, is it even breakable?
                raise Exception(
                    f"Expected item at the end of the chain, found None for {self.name}@and_then"
                )

            # Then, call in the next chain
            iter_v = self._wrap(next(final_u), name=next_name)
            async for v in iter_v:
                yield v

        return Chain[T, V](next_name, and_then)

    def gather(
        self: "Union[SingleOutputChain[T, List[AsyncGenerator[ChainOutput[V], Any]]], SingleOutputChain[T, List[AsyncGenerator[V, Any]]]]",
    ) -> "SingleOutputChain[T, List[List[V]]]":
        """
        Similar to `Chain.gather`, this method waits for all the async generators in the list returned by the chain to finish and gathers their results in a list.

        For detailed examples, refer to the documentation of `Chain.gather`.
        """

        next_name = f"{self.name}@gather"

        async def gather(
            input: T,
        ) -> AsyncGenerator[ChainOutput[List[List[V]]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the last result when it is done
            final_u: Optional[
                Union[
                    List[AsyncGenerator[ChainOutput[V], Any]],
                    List[AsyncGenerator[V, Any]],
                ]
            ] = None

            # TODO: try to work out why the type signature of self(input) is not fitting in there, it should
            async for value, to_reyield in self._reyield(
                cast(Any, self(input)), "gather"
            ):
                yield cast(ChainOutput[List[List[V]]], to_reyield)
                final_u = value

            if final_u is None:
                # TODO: try to make this happen with a bad use case, is it even breakable?
                raise Exception(
                    f"Expected item at the end of the chain, found None for {self.name}@gather"
                )

            async def consume_async_generator(
                generator: AsyncGenerator[X, Any],
            ) -> Iterable[X]:
                return [item async for item in generator]

            # TODO: should we really wait for everything to arrive before calling asyncio gather? Can we call it during the previous reyield?
            vss: Union[
                List[List[ChainOutput[V]]], List[List[V]]
            ] = await asyncio.gather(*(consume_async_generator(gen) for gen in final_u))

            clean_vss: List[List[V]] = []
            for vs in vss:
                clean_vs: List[V] = []
                for v in vs:
                    v_rewrapped = cast(
                        ChainOutput[List[List[V]]],
                        self._output_wrap(v, final=False),
                    )
                    if isinstance(v, ChainOutput):
                        yield v_rewrapped
                        if v.final:
                            clean_vs.append(v.data)
                    else:
                        clean_vs.append(v)
                clean_vss.append(clean_vs)

            yield self._output_wrap(clean_vss, name=next_name)

        return SingleOutputChain[T, List[List[V]]](next_name, gather)

    def on_error(
        self,
        handler: Callable[[Exception], Union[AsyncGenerator[ChainOutput[V], Any], V]],
    ) -> "SingleOutputChain[T, Union[U, V]]":
        """
        Similar to `Chain.on_error`, this method handles any uncaught exceptions that might occur during the execution of the current chain.

        For detailed examples, refer to the documentation of `Chain.gather`.
        """

        next_name = f"{self.name}@on_error"
        if hasattr(next, "name"):
            next_name = next.name

        async def on_error(
            input: T,
        ) -> AsyncGenerator[ChainOutput[Union[U, V]], Any]:
            try:
                async for output in self(input):
                    yield cast(ChainOutput[Union[U, V]], output)
            except Exception as e:
                async for output in self._wrap(handler(e), name=next_name):
                    yield cast(ChainOutput[Union[U, V]], output)

        return SingleOutputChain[T, Union[U, V]](
            next_name, lambda input: on_error(input)
        )
