from typing import Any, Optional, TypeVar, Union, cast

T = TypeVar("T")
U = TypeVar("U")


def unwrap(val: Optional[T]) -> T:
    return cast(T, val)
