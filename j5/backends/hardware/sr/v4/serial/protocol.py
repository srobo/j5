"""Common functionality between SR V4 boards."""
import re
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
        response = self.query("*IDN?")
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

    def _check_firmware_version_supported(
        self,
        version: str,
        minimum_fw_version: int = 4,
    ) -> None:
        """
        Raises an exception if the firmware version is not supported.

        :param version: the firmware version string to check.
        :param minimum_fw_version: the lowest supported major firmware version
        :raises CommunicationError: the board is running unsupported firmware
        """
        match = re.match(r"^(\d+)\.(\d+)$", version)
        if not match:
            raise CommunicationError(f"Unable to parse version number: {version}")

        hw_ver, fw_major_ver = match.groups()
        if hw_ver != "4":
            raise CommunicationError(
                f"Expected hardware version number to be 4, got {hw_ver}",
            )

        if int(fw_major_ver) < minimum_fw_version:
            raise CommunicationError(
                f"Expected major version number of at least {minimum_fw_version},"
                f" got {fw_major_ver}",
            )

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

    def query(self, command: str) -> str:
        """
        Sends a query to the board and returns its response as a string.

        This method expects a response with additional data
        and will raise an exception if only an ACK is received.

        Query commands end with '?'.

        :param command: The command to be sent as part of the query.
        :returns: Response.
        :raises CommunicationError: Failed to send request or only ACK is returned.
        """
        response = self.request(command)
        if response is not None:
            return response
        else:
            raise CommunicationError("Power board responded with ACK but expected data.")
