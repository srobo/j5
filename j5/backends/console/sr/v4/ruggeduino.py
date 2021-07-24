"""Console Backend for the SR v4 Ruggeduino."""

from typing import Set, cast

from j5.backends.console.j5.arduino import ArduinoConsoleBackend
from j5.boards import Board
from j5.boards.sr.v4 import Ruggeduino
from j5.components import StringCommandComponentInterface


class SRV4RuggeduinoConsoleBackend(
    StringCommandComponentInterface,
    ArduinoConsoleBackend,
):
    """Console Backend for the SR v4 Ruggeduino."""

    board = Ruggeduino

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        return {cast(Board, Ruggeduino("SERIAL", cls("SERIAL")))}

    def execute_string_command(self, command: str) -> str:
        """
        Execute the string command and return the result.

        This function can be synchronous and blocking.

        :param command: command to send.
        :returns: result from the command.
        """
        return self._console.read(
            f"Response to string command \"{command}\" [str]: ",
        )
