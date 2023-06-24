from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    TypeVar,
    Union,
)

from litechain.utils.async_iterable import as_async_iterable, collect, join

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class BaseChain(Generic[T, U]):
    _call: Callable[[T], U]

    def __init__(self, call: Callable[[T], U]) -> None:
        self._call = call

    def __call__(self, input: T) -> U:
        return self._call(input)

    def map(self, fn: Callable[[U], V]) -> "BaseChain[T, V]":
        """
        Maps the results without extracing them of the wrapper (Awaitable, AwaitableIterator),
        allowing you to map value on the fly
        """
        return self.__class__(lambda input: fn(self(input)))

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
    _call: Callable[[T], Union[AsyncIterable[U], U]]

    def __init__(self, call: Callable[[T], Union[AsyncIterable[U], U]]) -> None:
        self._call = call

    def __call__(self, input: T) -> AsyncIterable[U]:
        result = self._call(input)
        if isinstance(result, AsyncIterable):
            return result

        return as_async_iterable(result)

    def map(self, fn: Callable[[U], V]) -> "Chain[T, V]":
        async def map(input: T) -> AsyncIterable[V]:
            async for u in self(input):
                yield fn(u)

        return Chain[T, V](lambda input: map(input))

    def and_then(
        self, next: Callable[[Iterable[U]], AsyncIterable[V]]
    ) -> "Chain[T, V]":
        async def and_then(input: T) -> AsyncIterable[V]:
            u = await collect(self(input))
            async for v in next(u):
                yield v

        return Chain[T, V](and_then)

    def join(self: "Chain[T, str]", join_with="") -> "SingleOutputChain[T, str]":
        async def _join(input: T) -> str:
            u = await join(self(input), join_with)
            return u

        return SingleOutputChain[T, str](_join)


class SingleOutputChain(BaseChain[T, U]):
    call: Callable[[T], Union[Awaitable[U], U]]

    def __init__(self, call: Callable[[T], Union[Awaitable[U], U]]) -> None:
        self.call = call

    def __call__(self, input: T) -> Awaitable[U]:
        async def as_awaitable(value: V) -> V:
            return value

        result = self.call(input)
        if isinstance(result, Awaitable):
            return result
        return as_awaitable(result)

    def map(self, fn: Callable[[U], V]) -> "SingleOutputChain[T, V]":
        async def map(input: T) -> V:
            return fn(await self(input))

        return SingleOutputChain[T, V](call=lambda input: map(input))

    def and_then(self, next: Callable[[U], AsyncIterable[V]]) -> "Chain[T, V]":
        async def and_then(input: T) -> AsyncIterable[V]:
            u = await self(input)
            async for v in next(u):
                yield v

        return Chain[T, V](call=and_then)
