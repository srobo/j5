"""The Console Environment."""

from typing import Callable, Optional, Type, TypeVar

from j5.backends import Environment

ConsoleEnvironment = Environment("ConsoleEnvironment")

T = TypeVar("T")


class Console:
    """A helper class for the console environment."""

    def __init__(
            self,
            descriptor: str,
            print_function: Callable = print,  # type: ignore
            input_function: Callable = input,  # type: ignore
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
            return_type: Optional[Type[T]] = str,
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
