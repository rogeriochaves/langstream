from typing import Any, AsyncIterable, Iterable, TypeVar, cast

from litechain.core.chain import ChainOutput
from litechain.utils.async_iterable import collect, join

T = TypeVar("T")


async def filter_final_output(
    async_iterable: AsyncIterable[ChainOutput[T, Any]]
) -> AsyncIterable[T]:
    async for output in async_iterable:
        if output.final:
            yield cast(T, output.output)


async def join_final_output(
    async_iterable: AsyncIterable[ChainOutput[str, Any]]
) -> str:
    return await join(filter_final_output(async_iterable))


async def collect_final_output(
    async_iterable: AsyncIterable[ChainOutput[T, Any]]
) -> Iterable[T]:
    return await collect(filter_final_output(async_iterable))
