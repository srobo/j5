"""Helper classes for console backend tests."""

from typing import Optional, Type, TypeVar

from j5.backends.console import Console

T = TypeVar("T")


class MockConsole(Console):
    """Test Console for testing boards."""

    def __init__(self, descriptor: str) -> None:
        super(Console, self).__init__()
        self._descriptor = descriptor
        self.next_input: str = ""
        self.expects: str = ""

    def info(self, message: str) -> None:
        """Mock writing to the terminal."""
        assert message == self.expects

    def read(  # type: ignore
        self,
        prompt: str,
        return_type: Optional[Type[T]] = str,  # type: ignore
    ) -> Optional[T]:
        """Get a value of type 'return_type' from the user."""
        if return_type is not None:
            try:
                # We have to ignore the types on this function unfortunately,
                # as static type checking is not powerful enough to confirm
                # that it is correct at runtime.
                return return_type(self.next_input)  # type: ignore
            except ValueError:
                self.info(f"Unable to construct a {return_type.__name__}" f" from {self.next_input!r}")
        else:
            return None
