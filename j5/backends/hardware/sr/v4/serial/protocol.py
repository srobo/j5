"""Common functionality between SR V4 boards."""
import re
import threading
from abc import ABC
from typing import Collection, NamedTuple

from serial import SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware.j5.serial import SerialHardwareBackend


class BoardIdentity(NamedTuple):
    """Identifiers for a Student Robotics v4 board."""

    vendor: str
    board: str
    asset_tag: str
    software_version: str


class BoardVersion(NamedTuple):
    """The version returned from a board."""

    hw_ver: int
    fw_major: int
    fw_minor: int = 0


class SRV4SerialProtocolBackend(SerialHardwareBackend, ABC):
    """
    Backend for a Student Robotics v4 board using the serial protocol.

    The protocol is loosely based on SCPI.
    """

    _lock: threading.Lock

    @property
    def firmware_version(self) -> str:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        identity = self.get_identity()
        return identity.software_version

    def get_identity(self) -> BoardIdentity:
        """
        Get the board identity information.

        :raises CommunicationError: Response did not match the expected format.
        :returns: A tuple of board identity information
        """
        response = self.query("*IDN?")
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

    def request(self, command: str) -> None:
        """
        Sends a request to the board.

        A request command does not return any data and will respond
        ACK if the request was executed successfully.

        :param command: The command to be sent as part of the request.
        :raises CommunicationError: Failed to send request.
        """
        response = self._raw_request(command)

        if response != "ACK":
            raise CommunicationError(
                "Expected ACK from Power Board, but got: {response}",
            )

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
        response = self._raw_request(command)
        if response and response != "ACK":
            return response
        else:
            raise CommunicationError("Power board responded with ACK but expected data.")

    def _raw_request(self, command: str) -> str:
        """
        Make a raw protocol request to the board.

        If a NACK is received, an exception will be raised.

        :param command: The command to send to the board.
        :returns: The response from the board.
        :raises CommunicationError: The request was not successful.
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

        return response

    @staticmethod
    def _parse_float(data: str) -> float:
        """
        Parse a string as a floating point number.

        If the string is not a floating point number, raise an error.

        :param data: The string to parse.
        :returns: The parsed floating point number.
        :raises CommunicationError: The data was not a float.
        """
        try:
            return float(data)
        except TypeError as e:
            raise CommunicationError(
                f"Power board returned {data}, but expected a float",
            ) from e

    @staticmethod
    def _parse_version_string(version: str) -> BoardVersion:
        """
        Parse the version string.

        If the minor version is not present, it is assumed to be 0.

        :param version: The version string.
        :returns: A parsed version string.
        :raises ValueError: The version string was not valid.
        """
        match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", version)
        if not match:
            raise ValueError(f"Version does not match format: {version}")

        version_parts = (int(x) for x in match.groups(0))
        return BoardVersion(*version_parts)

    def _check_firmware_version_supported(
        self,
        version_string: str,
        supported_fw_versions: Collection[int],
    ) -> None:
        """
        Raises an exception if the firmware version is not supported.

        :param version_string: the firmware version string to check.
        :param supported_fw_versions: collection of supported major fw versions
        :raises CommunicationError: the board is running unsupported firmware
        """
        try:
            version = self._parse_version_string(version_string)
        except ValueError as e:
            raise CommunicationError(f"Unable to parse version number: {version}") from e

        if version.hw_ver != 4:
            raise CommunicationError(
                f"Expected hardware version number to be 4, got {version.hw_ver}",
            )

        if version.fw_major not in supported_fw_versions:
            raise CommunicationError(
                f"Expected major version number to be one of {supported_fw_versions},"
                f" got {version.fw_major}",
            )
