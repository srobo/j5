"""Utility classes and functions."""

from types import TracebackType
from typing import ContextManager, Optional, Type, TypeVar

T = TypeVar("T")


class NullContextManager(ContextManager[Optional[T]]):
    """
    A (typed) Python 3.6+ port of contextlib.nullcontext.

    https://docs.python.org/3/library/contextlib.html#contextlib.nullcontext
    """

    def __init__(self, enter_result: Optional[T] = None):
        self.enter_result = enter_result

    def __enter__(self) -> Optional[T]:
        return self.enter_result

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        pass
