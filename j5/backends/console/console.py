"""Console helper classes."""

from typing import Callable, Optional, Type, TypeVar

T = TypeVar("T")


class Console:
    """A helper class for console backends."""

    _DEFAULT_PRINT: Callable = print  # type: ignore  # noqa: T002
    _DEFAULT_INPUT: Callable = input  # type: ignore

    def __init__(
            self,
            descriptor: str,
            print_function: Callable = _DEFAULT_PRINT,  # type: ignore
            input_function: Callable = _DEFAULT_INPUT,  # type: ignore
    ) -> None:
        self._descriptor = descriptor
        self._print = print_function
        self._input = input_function

    def info(self, message: str) -> None:
        """Print information to the user."""
        self._print(f"{self._descriptor}: {message}")

    def read(  # type: ignore
            self,
            prompt: str,
            return_type: Optional[Type[T]] = str,  # type: ignore
    ) -> T:
        """Get a value of type 'return_type' from the user."""
        if return_type is not None:
            while True:
                response = self._input(f"{self._descriptor}: {prompt}: ")
                try:
                    # We have to ignore the types on this function unfortunately,
                    # as static type checking is not powerful enough to confirm
                    # that it is correct at runtime.
                    return return_type(response)  # type: ignore
                except ValueError:
                    self.info(f"Unable to construct a {return_type.__name__}"
                              f" from '{response}'")
        else:
            self._input(f"{self._descriptor}: {prompt}: ")
