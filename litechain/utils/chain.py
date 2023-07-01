from typing import Any, AsyncGenerator, Iterable, TypeVar, cast

from litechain.core.chain import ChainOutput
from litechain.utils.async_generator import collect, join

T = TypeVar("T")


async def filter_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T, Any], Any]
) -> AsyncGenerator[T, Any]:
    async for output in async_iterable:
        if output.final:
            yield cast(T, output.output)


async def join_final_output(
    async_iterable: AsyncGenerator[ChainOutput[str, Any], Any]
) -> str:
    return await join(filter_final_output(async_iterable))


async def collect_final_output(
    async_iterable: AsyncGenerator[ChainOutput[T, Any], Any]
) -> Iterable[T]:
    return await collect(filter_final_output(async_iterable))
