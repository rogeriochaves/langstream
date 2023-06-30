from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    AsyncIterable,
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

from litechain.utils.async_iterable import as_async_iterable

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
X = TypeVar("X")


@dataclass
class ChainOutput(Generic[T, V]):
    chain: str
    output: V
    final: bool


# TODO: not needed
class BaseChain(ABC, Generic[T, U]):
    name: str
    _call: Callable[[T], U]

    @abstractmethod
    def __init__(self, name: str, call: Callable[[T], U]) -> None:
        self.name = name
        self._call = call

    @abstractmethod
    def __call__(self, input: T) -> ChainOutput[U, W]:
        result = self._call(input)
        return self._wrap(result)

    @abstractmethod
    def _wrap(self, value: U) -> ChainOutput[U, W]:
        return self._output_wrap(value)

    def _output_wrap(
        self, value: Union[ChainOutput[V, W], V], final=None, name=None
    ) -> ChainOutput[V, Union[V, W]]:
        if isinstance(value, ChainOutput):
            final = final if final is not None else value.final
            return ChainOutput[V, Union[V, W]](
                chain=value.chain, output=value.output, final=final
            )

        final = final if final is not None else True
        return ChainOutput[V, Union[V, W]](
            chain=self.name if name is None else name, output=value, final=final
        )

    @abstractmethod
    def map(self, fn: Callable[[U], V]) -> "BaseChain[T, V]":
        """
        Maps the results without extracing them of the wrapper (Awaitable, AwaitableIterator),
        allowing you to map value on the fly
        """
        return self.__class__(self.name, lambda input: fn(self(input).output))

    @abstractmethod
    def and_then(self, next: Callable[[U], V]) -> "BaseChain[T, V]":
        """
        Extracts the results outside it's wrapper box (Awaitable, AwaitableIterator) and then map it.
        On the base class, since there is no wrapper, it works exactly as map
        """
        return self.map(next)

    def join(self: "BaseChain[T, str]", join_with="") -> "BaseChain[T, str]":
        """
        If the chain produces string, waits for all of them to arrive and concatenate it all
        """
        return self


class Chain(BaseChain[T, U]):
    _call: Callable[[T], Union[AsyncIterable[ChainOutput[U, Any]], AsyncIterable[U], U]]

    def __init__(
        self,
        name: str,
        call: Callable[
            [T], Union[AsyncIterable[ChainOutput[U, W]], AsyncIterable[U], U]
        ],
    ) -> None:
        self.name = name
        self._call = call

    def __call__(self, input: T) -> AsyncIterable[ChainOutput[U, Union[U, Any]]]:
        result = self._call(input)
        return self._wrap(result)

    def _wrap(
        self,
        value: Union[AsyncIterable[ChainOutput[V, W]], AsyncIterable[V], V],
        name: Optional[str] = None,
    ) -> AsyncIterable[ChainOutput[V, Union[V, W]]]:
        async def _wrap(
            values: Union[AsyncIterable[ChainOutput[V, W]], AsyncIterable[V]],
        ) -> AsyncIterable[ChainOutput[V, Union[V, W]]]:
            async for value in values:
                yield self._output_wrap(value, name=name)

        if isinstance(value, AsyncIterable):
            return _wrap(value)
        return _wrap(as_async_iterable(value))

    async def _reyield(
        self, async_iterable: AsyncIterable[ChainOutput[U, U]]
    ) -> AsyncIterable[Tuple[List[U], ChainOutput[U, U]]]:
        values: List[U] = []
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                values.append(u.output)
            yield (values, u_rewrapped)

    def map(self, fn: Callable[[U], V]) -> "Chain[T, V]":
        async def map(input: T) -> AsyncIterable[ChainOutput[V, Union[U, V]]]:
            # Reyield previous chain so we never block the stream, and at the same time yield mapped values
            prev_len_values = 0
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[V, Union[U, V]], to_reyield)
                if len(values) > prev_len_values:  # as soon as there is a new value
                    prev_len_values = len(values)
                    yield cast(ChainOutput[V, Union[U, V]], fn(values[-1]))

        return Chain[T, V](f"{self.name}@map", lambda input: map(input))

    def and_then(
        self, next: Callable[[Iterable[U]], Union[AsyncIterable[ChainOutput[V, W]], V]]
    ) -> "Chain[T, V]":
        next_name = f"{self.name}@and_then"
        if hasattr(next, "name"):
            next_name = next.name

        async def and_then(
            input: T,
        ) -> AsyncIterable[ChainOutput[V, Union[U, V]]]:
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
        async def _collect(
            input: T,
        ) -> AsyncIterable[ChainOutput[List[U], Union[U, List[U]]]]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[U] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[List[U], Union[U, List[U]]], to_reyield)
                iter_u = values

            # Then, yield the collected results
            yield cast(ChainOutput[List[U], Union[U, List[U]]], iter_u)

        return SingleOutputChain[T, List[U]](f"{self.name}@collect", _collect)

    def join(self: "Chain[T, str]", join_with="") -> "SingleOutputChain[T, str]":
        async def _join(
            input: T,
        ) -> AsyncIterable[ChainOutput[str, Union[U, str]]]:
            # First, reyield previous chain so we never block the stream, and collect the results until they are done
            iter_u: Iterable[str] = []
            async for values, to_reyield in self._reyield(self(input)):
                yield cast(ChainOutput[str, Union[U, str]], to_reyield)
                iter_u = values

            # Then, return the joined result
            output: str = join_with.join(iter_u)
            yield cast(ChainOutput[str, Union[U, str]], output)

        return SingleOutputChain[T, str](f"{self.name}@join", _join)

    def gather(
        self: "Chain[T, List[AsyncIterable[V]]]",
    ) -> "Chain[T, List[V]]":
        # TODO
        raise NotImplementedError


class SingleOutputChain(Chain[T, U]):
    _call: Callable[[T], Union[AsyncIterable[ChainOutput[U, Any]], AsyncIterable[U], U]]

    async def _reyield(
        self, async_iterable: AsyncIterable[ChainOutput[U, U]], at: str
    ) -> AsyncIterable[Tuple[Optional[U], ChainOutput[U, U]]]:
        final_value: Optional[U] = None
        async for u in async_iterable:
            u_rewrapped = self._output_wrap(u, final=False)
            if u.final:
                if final_value is not None:
                    # TODO: try to make this happen with a bad use case, is it even breakable?
                    raise Exception(
                        f"Expected a single item at the end of SingleOutputChain, found multiple for {self.name}@{at}"
                    )
                final_value = u.output
            yield (final_value, u_rewrapped)

    def and_then(
        self, next: Callable[[U], Union[AsyncIterable[ChainOutput[V, W]], V]]
    ) -> "Chain[T, V]":
        next_name = f"{self.name}@and_then"
        # TODO: hasattr(next, "name")

        async def and_then(
            input: T,
        ) -> AsyncIterable[ChainOutput[V, Union[U, V]]]:
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

        # TODO: next_name
        return Chain[T, V](next_name, and_then)

    def gather(
        self: "Union[SingleOutputChain[T, List[AsyncIterable[ChainOutput[V, W]]]], SingleOutputChain[T, List[AsyncIterable[V]]]]",
    ) -> "SingleOutputChain[T, List[List[V]]]":
        async def gather(
            input: T,
        ) -> AsyncIterable[ChainOutput[List[List[V]], Union[U, List[List[V]]]]]:
            # First, reyield previous chain so we never block the stream, and collect the last result when it is done
            final_u: Optional[
                Union[List[AsyncIterable[ChainOutput[V, W]]], List[AsyncIterable[V]]]
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

            async def consume_async_generator(generator: AsyncIterable[X]) -> Iterable[X]:
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
                            clean_vs.append(v.output)
                    else:
                        clean_vs.append(v)
                clean_vss.append(clean_vs)

            yield cast(ChainOutput[List[List[V]], Union[U, List[List[V]]]], clean_vss)

        return SingleOutputChain[T, List[List[V]]](f"{self.name}@gather", gather)


