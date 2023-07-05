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
class ChainOutput(Generic[T, V]):
    """
    ChainOutput is a data class that represents the output of a Chain at each step.

    Attributes
    ----------
    chain : str
        The name of the chain that produced this output. This helps in identifying
        which part of the processing pipeline the output is coming from.

    output : V
        The actual output data produced by the Chain. This can be of any type produced by any step of the whole Chain.

    final : bool
        A boolean flag indicating whether this output is the final output of the Chain.
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
    data: V
    final: bool


class Chain(Generic[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[ChainOutput[U, Any], Any], AsyncGenerator[U, Any], U]
    ]

    def __init__(
        self,
        name: str,
        call: Callable[
            [T],
            Union[AsyncGenerator[ChainOutput[U, W], Any], AsyncGenerator[U, Any], U],
        ],
    ) -> None:
        self.name = name
        self._call = call

    def __call__(self, input: T) -> AsyncGenerator[ChainOutput[U, Union[U, Any]], Any]:
        result = self._call(input)
        return self._wrap(result)

    def _wrap(
        self,
        value: Union[AsyncGenerator[ChainOutput[V, W], Any], AsyncGenerator[V, Any], V],
        name: Optional[str] = None,
    ) -> AsyncGenerator[ChainOutput[V, Union[V, W]], Any]:
        async def _wrap(
            values: Union[
                AsyncGenerator[ChainOutput[V, W], Any], AsyncGenerator[V, Any]
            ],
        ) -> AsyncGenerator[ChainOutput[V, Union[V, W]], Any]:
            async for value in values:
                yield self._output_wrap(value, name=name)

        if isinstance(value, AsyncGenerator):
            return _wrap(value)
        return _wrap(as_async_generator(value))

    def _output_wrap(
        self, value: Union[ChainOutput[V, W], V], final=None, name=None
    ) -> ChainOutput[V, Union[V, W]]:
        if isinstance(value, ChainOutput):
            final = final if final is not None else value.final
            return ChainOutput[V, Union[V, W]](
                chain=value.chain, data=value.data, final=final
            )

        final = final if final is not None else True
        return ChainOutput[V, Union[V, W]](
            chain=self.name if name is None else name, data=value, final=final
        )

    async def _reyield(
        self, async_iterable: AsyncGenerator[ChainOutput[U, U], Any]
    ) -> AsyncGenerator[Tuple[List[U], ChainOutput[U, U]], Any]:
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

        async def map(input: T) -> AsyncGenerator[ChainOutput[V, Union[U, V]], Any]:
            # Reyield previous chain so we never block the stream, and at the same time yield mapped values
            prev_len_values = 0
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[V, Union[U, V]], to_reyield)
                if len(values) > prev_len_values:  # as soon as there is a new value
                    prev_len_values = len(values)
                    yield cast(ChainOutput[V, Union[U, V]], fn(values[-1]))

        return Chain[T, V](f"{self.name}@map", lambda input: map(input))

    def and_then(
        self,
        next: Callable[[Iterable[U]], Union[AsyncGenerator[ChainOutput[V, W], Any], V]],
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
        ) -> AsyncGenerator[ChainOutput[V, Union[U, V]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[V, Union[U, V]], to_reyield)
                iter_u = values

            # Then, call in the next chain
            iter_v = self._wrap(next(iter_u), name=next_name)
            async for v in iter_v:
                yield cast(ChainOutput[V, Union[U, V]], v)

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

        async def _collect(
            input: T,
        ) -> AsyncGenerator[ChainOutput[List[U], Union[U, List[U]]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[List[U], Union[U, List[U]]], to_reyield)
                iter_u = values

            # Then, yield the collected results
            yield cast(ChainOutput[List[U], Union[U, List[U]]], iter_u)

        return SingleOutputChain[T, List[U]](f"{self.name}@collect", _collect)

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

        async def _join(
            input: T,
        ) -> AsyncGenerator[ChainOutput[str, Union[U, str]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[str] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[str, Union[U, str]], to_reyield)
                iter_u = values

            # Then, return the joined result
            output: str = separator.join(iter_u)
            yield cast(ChainOutput[str, Union[U, str]], output)

        return SingleOutputChain[T, str](f"{self.name}@join", _join)

    def gather(
        self: "Union[Chain[T, AsyncGenerator[ChainOutput[V, W], Any]], Chain[T, AsyncGenerator[V, Any]]]",
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


class SingleOutputChain(Chain[T, U]):
    """"""

    _call: Callable[
        [T], Union[AsyncGenerator[ChainOutput[U, Any], Any], AsyncGenerator[U, Any], U]
    ]

    async def _reyield(
        self, async_iterable: AsyncGenerator[ChainOutput[U, U], Any], at: str
    ) -> AsyncGenerator[Tuple[Optional[U], ChainOutput[U, U]], Any]:
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

        async def map(input: T) -> AsyncGenerator[ChainOutput[V, Union[U, V]], Any]:
            # Reyield previous chain so we never block the stream, and at the same time yield mapped values
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input), "map"):
                yield cast(ChainOutput[V, Union[U, V]], to_reyield)
                final_u = value

            if final_u is None:
                # TODO: try to make this happen with a bad use case, is it even breakable?
                raise Exception(
                    f"Expected item at the end of the chain, found None for {self.name}@map"
                )
            yield cast(ChainOutput[V, Union[U, V]], fn(final_u))

        return SingleOutputChain[T, V](f"{self.name}@map", lambda input: map(input))

    def and_then(
        self,
        next: Callable[
            [U],
            Union[AsyncGenerator[ChainOutput[V, W], Any], AsyncGenerator[V, Any], V],
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
        ) -> AsyncGenerator[ChainOutput[V, Union[U, V]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the last result when it is done
            final_u: Optional[U] = None
            async for value, to_reyield in self._reyield(self(input), "and_then"):
                yield cast(ChainOutput[V, Union[U, V]], to_reyield)
                final_u = value

            if final_u is None:
                # TODO: try to make this happen with a bad use case, is it even breakable?
                raise Exception(
                    f"Expected item at the end of the chain, found None for {self.name}@and_then"
                )

            # Then, call in the next chain
            iter_v = self._wrap(next(final_u), name=next_name)
            async for v in iter_v:
                yield cast(ChainOutput[V, Union[U, V]], v)

        return Chain[T, V](next_name, and_then)

    def gather(
        self: "Union[SingleOutputChain[T, List[AsyncGenerator[ChainOutput[V, W], Any]]], SingleOutputChain[T, List[AsyncGenerator[V, Any]]]]",
    ) -> "SingleOutputChain[T, List[List[V]]]":
        """
        Similar to `Chain.gather`, this method waits for all the async generators in the list returned by the chain to finish and gathers their results in a list.

        For detailed examples, refer to the documentation of `Chain.gather`.
        """

        async def gather(
            input: T,
        ) -> AsyncGenerator[ChainOutput[List[List[V]], Union[U, List[List[V]]]], Any]:
            # First, reyield previous chain so we never block the stream, and collect the last result when it is done
            final_u: Optional[
                Union[
                    List[AsyncGenerator[ChainOutput[V, W], Any]],
                    List[AsyncGenerator[V, Any]],
                ]
            ] = None

            # TODO: try to work out why the type signature of self(input) is not fitting in there, it should
            async for value, to_reyield in self._reyield(
                cast(Any, self(input)), "gather"
            ):
                yield cast(
                    ChainOutput[List[List[V]], Union[U, List[List[V]]]], to_reyield
                )
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
                List[List[ChainOutput[V, W]]], List[List[V]]
            ] = await asyncio.gather(*(consume_async_generator(gen) for gen in final_u))

            clean_vss = []
            for vs in vss:
                clean_vs = []
                for v in vs:
                    v_rewrapped = cast(
                        ChainOutput[List[List[V]], Union[U, List[List[V]]]],
                        self._output_wrap(v, final=False),
                    )
                    if isinstance(v, ChainOutput):
                        yield v_rewrapped
                        if v.final:
                            clean_vs.append(v.data)
                    else:
                        clean_vs.append(v)
                clean_vss.append(clean_vs)

            yield cast(ChainOutput[List[List[V]], Union[U, List[List[V]]]], clean_vss)

        return SingleOutputChain[T, List[List[V]]](f"{self.name}@gather", gather)
