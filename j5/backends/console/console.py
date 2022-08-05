"""Console helper classes."""
import sys
from typing import Dict, Optional, Type, TypeVar

T = TypeVar("T")


class Console:
    """A helper class for console backends."""

    def __init__(self, descriptor: str) -> None:
        self._descriptor = descriptor

    def _print(self, string: str) -> None:
        """
        Wrapper around print.

        :param string: String to print.
        """
        print(string)  # noqa: T201

    def _input(self, prompt: str) -> str:
        """
        Wrapper around input.

        :param prompt: prompt for user.
        :returns: response from user.
        """
        return input(prompt)

    def info(self, message: str) -> None:
        """
        Print information to the user.

        :param message: Message to print to the user.
        """
        self._print(f"{self._descriptor}: {message}")

    def read(  # type: ignore
            self,
            prompt: str,
            return_type: Optional[Type[T]] = str,  # type: ignore
            check_stdin: bool = True,
    ) -> T:
        """
        Prompt the user for a value of type 'return_type'.

        :param prompt: Prompt to display to the user.
        :param return_type: type to cast the input as, defaults to str.
        :param check_stdin: Check if stdin is available is a tty.
        :returns: value of type 'return_type'.
        """
        if check_stdin and return_type is bool and not sys.stdin.isatty():
            return False  # type: ignore
        elif return_type is not None:
            while True:
                response = self._input(f"{self._descriptor}: {prompt}: ")
                try:
                    # We have to ignore the types on this function unfortunately,
                    # as static type checking is not powerful enough to confirm
                    # that it is correct at runtime.
                    if return_type == bool:
                        return self._get_bool(response)  # type: ignore
                    return return_type(response)  # type: ignore
                except ValueError:
                    self.info(f"Unable to construct a {return_type.__name__}"
                              f" from '{response}'")
        else:
            self._input(f"{self._descriptor}: {prompt}: ")

    @staticmethod
    def _get_bool(case: str) -> bool:
        """
        Check if a string is a bool, if so return it.

        :param case: string to check.
        :return: boolean representation of case
        :raises ValueError: case is not a bool.
        """
        response_map: Dict[str, bool] = {
            "true": True,
            "yes": True,
            "false": False,
            "no": False,
        }
        normalised = case.lower().strip()
        if normalised not in response_map:
            raise ValueError()
        else:
            return response_map[normalised]
