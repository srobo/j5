"""
Type stubs for pytest.
Note that stubs are only written for the parts that we use.
"""

from typing import Any, ContextManager, Optional, Pattern, Tuple, Type, TypeVar, Union

from _pytest._code import ExceptionInfo

_E = TypeVar("_E", bound=BaseException)

def raises(
    expected_exception: Union["Type[_E]", Tuple["Type[_E]", ...]],
    *args: Any,
    match: Optional[Union[str, Pattern[Any]]] = None,
    **kwargs: Any
) -> ContextManager[Optional[ExceptionInfo]]: ...
