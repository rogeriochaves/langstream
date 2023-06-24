from abc import ABC, abstractmethod
import asyncio
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    TypeVar,
    Union,
)

from litechain.utils.async_iterable import as_async_iterable, collect, join

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class BaseChain(ABC, Generic[T, U]):
    _call: Callable[[T], U]

    @abstractmethod
    def __init__(self, call: Callable[[T], U]) -> None:
        self._call = call

    @abstractmethod
    def __call__(self, input: T) -> U:
        result = self._call(input)
        return self._wrap(result)

    @abstractmethod
    def _wrap(self, value: U) -> U:
        return value

    @abstractmethod
    def map(self, fn: Callable[[U], V]) -> "BaseChain[T, V]":
        """
        Maps the results without extracing them of the wrapper (Awaitable, AwaitableIterator),
        allowing you to map value on the fly
        """
        return self.__class__(lambda input: fn(self(input)))

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
    _call: Callable[[T], Union[AsyncIterable[U], U]]

    def __init__(self, call: Callable[[T], Union[AsyncIterable[U], U]]) -> None:
        self._call = call

    def __call__(self, input: T) -> AsyncIterable[U]:
        result = self._call(input)
        return self._wrap(result)

    def _wrap(self, value: Union[AsyncIterable[V], V]) -> AsyncIterable[V]:
        if isinstance(value, AsyncIterable):
            return value
        return as_async_iterable(value)

    def map(self, fn: Callable[[U], V]) -> "Chain[T, V]":
        async def map(input: T) -> AsyncIterable[V]:
            async for u in self(input):
                yield fn(u)

        return Chain[T, V](lambda input: map(input))

    def and_then(
        self, next: Callable[[Iterable[U]], Union[AsyncIterable[V], V]]
    ) -> "Chain[T, V]":
        async def and_then(input: T) -> AsyncIterable[V]:
            u = await collect(self(input))
            iter_v = self._wrap(next(u))
            async for v in iter_v:
                yield v

        return Chain[T, V](and_then)

    def collect(self: "Chain[T, U]") -> "SingleOutputChain[T, List[U]]":
        async def _collect(input: T) -> List[U]:
            u = await collect(self(input))
            return u

        return SingleOutputChain[T, List[U]](_collect)

    def join(self: "Chain[T, str]", join_with="") -> "SingleOutputChain[T, str]":
        async def _join(input: T) -> str:
            u = await join(self(input), join_with)
            return u

        return SingleOutputChain[T, str](_join)

    def gather(
        self: "Chain[T, List[AsyncIterable[V]]]",
    ) -> "Chain[T, List[V]]":
        # TODO
        raise NotImplementedError


class SingleOutputChain(BaseChain[T, U]):
    call: Callable[[T], Union[Awaitable[U], U]]

    def __init__(self, call: Callable[[T], Union[Awaitable[U], U]]) -> None:
        self.call = call

    def __call__(self, input: T) -> Awaitable[U]:
        result = self.call(input)
        return self._wrap(result)

    def _wrap(self, value: Union[Awaitable[V], V]) -> Awaitable[V]:
        async def as_awaitable(value: V) -> V:
            return value

        if isinstance(value, Awaitable):
            return value
        return as_awaitable(value)

    def map(self, fn: Callable[[U], V]) -> "SingleOutputChain[T, V]":
        async def map(input: T) -> V:
            return fn(await self(input))

        return SingleOutputChain[T, V](lambda input: map(input))

    def and_then(self, next: Callable[[U], AsyncIterable[V]]) -> "Chain[T, V]":
        async def and_then(input: T) -> AsyncIterable[V]:
            u = await self(input)
            async for v in next(u):
                yield v

        return Chain[T, V](and_then)

    def gather(
        self: "Union[SingleOutputChain[T, List[Awaitable[V]]], SingleOutputChain[T, List[Coroutine[Any, Any, V]]]]",
    ) -> "Chain[T, V]":
        async def gather(input: T) -> AsyncIterable[V]:
            vs: List[V] = await asyncio.gather(*await self(input))
            for v in vs:
                yield v

        return Chain[T, V](gather)
