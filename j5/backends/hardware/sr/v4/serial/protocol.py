"""Common functionality between SR V4 boards."""
import threading
from abc import ABC
from typing import NamedTuple, Optional

from serial import SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware.j5.serial import SerialHardwareBackend


class BoardIdentity(NamedTuple):
    """Identifiers for a Student Robotics v4 board."""

    vendor: str
    board: str
    asset_tag: str
    software_version: str


class SRV4SerialProtocolBackend(SerialHardwareBackend, ABC):
    """Backend for a Student Robotics v4 board using the serial protocol."""

    _lock: threading.Lock

    def get_identity(self) -> BoardIdentity:
        """
        Get the board identity information.

        :raises CommunicationError: Response did not match the expected format.
        :returns: A tuple of board identity information
        """
        response = self.request("*IDN?")
        if response is None:
            raise CommunicationError("Power board responded with ACK but expected data.")
        parts = response.split(":", 4)
        if len(parts) != 4:
            raise CommunicationError(
                f"Identify response did not match format: {response}")
        else:
            return BoardIdentity(*parts)

    def reset_board(self) -> None:
        """
        Resets the board.

        This turns off all the board's outputs, LEDs, etc.
        """
        self.request("*RESET")

    @property
    def firmware_version(self) -> str:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        identity = self.get_identity()
        return identity.software_version

    def check_firmware_version_supported(self) -> None:
        """
        Raises an exception if the firmware version is not supported.

        :raises NotImplementedError: power board is running unsupported firmware
        """
        version = self.firmware_version
        if not version.startswith("4."):
            raise NotImplementedError(f"This power board is running firmware "
                                      f"version {version},"
                                      "but only version 4.x is supported.")

    def request(self, command: str) -> Optional[str]:
        """
        Sends a request to the board.

        :param command: The command to be sent as part of the request.
        :returns: Response, if any.
        :raises CommunicationError: Failed to send request.
        """
        request_data = command.encode("ascii") + b'\n'

        with self._lock:
            try:
                bytes_written = self._serial.write(request_data)
                if len(request_data) != bytes_written:
                    raise CommunicationError(
                        "Mismatch in command bytes written to serial interface.",
                    )
            except SerialTimeoutException as e:
                raise CommunicationError(f"Serial Timeout Error: {e}") from e
            except SerialException as e:
                raise CommunicationError(f"Serial Error: {e}") from e

            response = self.read_serial_line()

        if response[:4] == "NACK":
            _, error_string = response.split(":", 1)
            raise CommunicationError(f"Power Board returned an error: {error_string}")

        expects_response = command[-1:] == "?"
        if expects_response:
            return response
        elif response == "ACK":
            return None
        else:
            raise CommunicationError("Expected ACK from Power Board,"
                                     f"but got: {response}")

    def request_with_response(self, command: str) -> str:
        """
        Sends a request to the board and returns its response as a string.

        This method expects a response with additional data
        and will raise an exception if only an ACK is received.

        :param command: The command to be sent as part of the request.
        :returns: Response.
        :raises ValueError: The command doesn't return a response.
        :raises CommunicationError: Failed to send request or only ACK is returned.
        """
        if not command.endswith('?'):
            raise ValueError(
                f"The provided command does not expect a response: {command}")

        response = self.request(command)
        if response is not None:
            return response
        else:
            raise CommunicationError("Power board responded with ACK but expected data.")
