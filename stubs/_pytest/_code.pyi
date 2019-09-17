"""
Type stubs for _pytest._code.

Only the signatures we need are included.
"""

from types import FrameType
from typing import Any, Optional, Type, TypeVar

_E = TypeVar("_E", bound=BaseException)

class ExceptionInfo:
    """ wraps sys.exc_info() objects and offers
        help for navigating the traceback.
    """

    @classmethod
    def from_current(cls, exprinfo: Optional[str] = None) -> "ExceptionInfo":
        """returns an ExceptionInfo matching the current traceback
        .. warning::
            Experimental API
        :param exprinfo: a text string helping to determine if we should
                         strip ``AssertionError`` from the output, defaults
                         to the exception message/``__str__()``
        """
        ...
    @classmethod
    def for_later(cls) -> "ExceptionInfo":
        """return an unfilled ExceptionInfo
        """
        ...
    @property
    def type(self) -> Type[_E]:
        """the exception class"""
        ...
    @property
    def value(self) -> Any:
        """the exception value"""
        ...
    @property
    def tb(self) -> FrameType:
        """the exception raw traceback"""
        ...
    @property
    def typename(self) -> str:
        """the type name of the exception"""
        ...
    def __repr__(self) -> str: ...
    def exconly(self, tryshort: bool = False) -> str:
        """ return the exception as a string
            when 'tryshort' resolves to True, and the exception is a
            _pytest._code._AssertionError, only the actual exception part of
            the exception representation is returned (so 'AssertionError: ' is
            removed from the beginning)
        """
        ...
    def errisinstance(self, exc: Any) -> bool:
        """ return True if the exception is an instance of exc """
        ...
