"""Tests for the Student Robotics Ruggeduino hardware implementation."""
from math import isclose
from typing import Optional, Type, cast

import pytest
from serial import Serial, SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware import NotSupportedByHardwareError
from j5.backends.hardware.sr.v4 import SRV4RuggeduinoHardwareBackend
from j5.boards.arduino import ArduinoUno
from j5.components import GPIOPinMode
from tests.backends.hardware.j5.mock_serial import MockSerial

# Pins on the digital-analogue border
EDGE_ANALOGUE_PIN = ArduinoUno.FIRST_ANALOGUE_PIN
EDGE_DIGITAL_PIN = EDGE_ANALOGUE_PIN - 1


class RuggeduinoSerial(MockSerial):
    """RuggeduinoSerial is the same as MockSerial, but includes expected received data."""

    expected_baudrate = 115200
    firmware_version = "1"

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: float = 1,
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
        )

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        if data == b"v":
            version_line: bytes = b"SRduino:" + self.firmware_version.encode("utf-8")
            self.append_received_data(version_line, newline=True)
        elif data == b"foo":
            self.append_received_data(data[::-1], newline=True)

    def check_data_sent_by_constructor(self) -> None:
        """Check that the backend constructor sent expected data to the serial port."""
        # Query version, then set all digital pins to input
        self.check_sent_data(b"vicidieifigihiiijikilimin")


class RuggeduinoSerialNoBoot(MockSerial):
    """Like MockSerial, but with a faster baudrate. Receives nothing on initialisation."""

    expected_baudrate = 115200


class RuggeduinoSerialBadVersion(RuggeduinoSerial):
    """Like RuggeduinoSerial, but reports a malformed version number."""

    firmware_version = "5"


class RuggeduinoSerialTimeout(RuggeduinoSerial):
    """Like RuggeduinoSerial, but times out when trying to write."""

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        raise SerialTimeoutException()


class RuggeduinoSerialException(RuggeduinoSerial):
    """Like RuggeduinoSerial, but raises a SerialException when trying to write."""

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        raise SerialException()


def make_backend(
    serial_class: Type[MockSerial] = RuggeduinoSerial,
) -> SRV4RuggeduinoHardwareBackend:
    """Instantiate an SBArduinoHardwareBackend  with some default arguments."""

    class EphemeralBackend(SRV4RuggeduinoHardwareBackend):
        def get_serial_class(self) -> Type[Serial]:
            return serial_class  # type: ignore

    return EphemeralBackend("COM0")


def test_backend_initialisation() -> None:
    """Test that we can initialise an SRV4RuggeduinoHardwareBackend."""
    backend = make_backend()
    assert backend.serial_port == "COM0"
    assert isinstance(backend._serial, RuggeduinoSerial)
    assert all(pin.mode is GPIOPinMode.DIGITAL_INPUT for pin in backend._digital_pins.values())
    assert all(pin.state is False for pin in backend._digital_pins.values())


def test_backend_initialisation_serial() -> None:
    """Test commands/responses are sent/received during initialisation."""
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    serial.check_all_received_data_consumed()

    with pytest.raises(CommunicationError):
        make_backend(RuggeduinoSerialNoBoot)


def test_backend_version_check() -> None:
    """Test that an exception is raised if the arduino reports an unsupported version."""
    with pytest.raises(CommunicationError):
        make_backend(RuggeduinoSerialBadVersion)


def test_backend_firmware_version() -> None:
    """Test that the firmware version is parsed correctly."""
    backend = make_backend()
    assert backend.firmware_version == RuggeduinoSerial.firmware_version


def test_backend_official_firmware() -> None:
    """Test that only "SRduino" represents official firmware."""
    backend = make_backend()
    assert backend.is_official_firmware is True
    backend._version_line = "SRcustom:1"
    assert backend.is_official_firmware is False


def test_backend_handles_bad_commands() -> None:
    """Test that an exception is raised when commands are longer than 1 character."""
    backend = make_backend()

    with pytest.raises(ValueError):
        backend._command("ghd")
    with pytest.raises(ValueError):
        backend._command("")


def test_backend_handles_serial_exeption() -> None:
    """Test that an exception is raised when a SerialException happens."""
    with pytest.raises(CommunicationError):
        make_backend(RuggeduinoSerialTimeout)
    with pytest.raises(CommunicationError):
        make_backend(RuggeduinoSerialException)


def test_backend_encode_pin() -> None:
    """Test that pin numbers are converted to letters properly."""
    assert SRV4RuggeduinoHardwareBackend.encode_pin(19) == "t"
    assert SRV4RuggeduinoHardwareBackend.encode_pin(None) == ""


def test_backend_update_digital_pin_requires_digital_pin() -> None:
    """Test that analogue pins are invalid for _update_digital_pin."""
    backend = make_backend()

    with pytest.raises(RuntimeError):
        backend._update_digital_pin(EDGE_ANALOGUE_PIN)


def test_backend_update_digital_pin_requires_pin_mode() -> None:
    """Test that analogue pin modes are invalid for _update_digital_pin."""
    pin = 2
    backend = make_backend()

    backend._digital_pins[pin].mode = GPIOPinMode.ANALOGUE_INPUT
    with pytest.raises(RuntimeError):
        backend._update_digital_pin(pin)


def check_sent_data(serial: RuggeduinoSerial, command: bytes, pin: Optional[int]) -> None:
    """Verify the data sent in a Ruggeduino command."""
    serial.check_sent_data(
        command + SRV4RuggeduinoHardwareBackend.encode_pin(pin).encode("utf-8"),
    )


def check_sent_data_dual_command(
    serial: RuggeduinoSerial,
    command1: bytes,
    command2: bytes,
    pin: int,
) -> None:
    """Verify the data sent in two sequential Ruggeduino commands."""
    pin_bytes = SRV4RuggeduinoHardwareBackend.encode_pin(pin).encode("utf-8")
    serial.check_sent_data(command1 + pin_bytes + command2 + pin_bytes)


def test_backend_write_digital_state() -> None:
    """Test that we can write the digital state of a pin."""
    pin = 2
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    # This should put the pin into the most recent (or default) output state.
    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    check_sent_data_dual_command(serial, b"o", b"l", pin)
    backend.write_gpio_pin_digital_state(pin, True)
    check_sent_data_dual_command(serial, b"o", b"h", pin)
    backend.write_gpio_pin_digital_state(pin, False)
    check_sent_data_dual_command(serial, b"o", b"l", pin)
    serial.check_all_received_data_consumed()


def test_backend_digital_state_persists() -> None:
    """Test switching to a different mode and then back to output."""
    pin = 2
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    check_sent_data_dual_command(serial, b"o", b"l", pin)

    backend.write_gpio_pin_digital_state(pin, False)
    check_sent_data_dual_command(serial, b"o", b"l", pin)

    backend.write_gpio_pin_digital_state(pin, True)
    check_sent_data_dual_command(serial, b"o", b"h", pin)

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT)
    check_sent_data(serial, b"i", pin)

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    check_sent_data_dual_command(serial, b"o", b"h", pin)

    backend.write_gpio_pin_digital_state(pin, True)
    check_sent_data_dual_command(serial, b"o", b"h", pin)

    backend.write_gpio_pin_digital_state(pin, False)
    check_sent_data_dual_command(serial, b"o", b"l", pin)

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT)
    check_sent_data(serial, b"i", pin)

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    check_sent_data_dual_command(serial, b"o", b"l", pin)

    serial.check_all_received_data_consumed()


def test_backend_input_modes() -> None:
    """Check that the correct commands are send when setting pins to input modes."""
    pin = 2
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT)
    check_sent_data(serial, b"i", pin)
    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT_PULLUP)
    check_sent_data(serial, b"p", pin)
    with pytest.raises(NotSupportedByHardwareError):
        backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT_PULLDOWN)
    serial.check_all_received_data_consumed()


def test_backend_read_digital_state() -> None:
    """Test that we can read the digital state of a pin."""
    pin = 2
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT)
    check_sent_data(serial, b"i", pin)

    serial.append_received_data(b"h", newline=True)
    assert backend.read_gpio_pin_digital_state(pin) is True
    check_sent_data(serial, b"r", pin)

    serial.append_received_data(b"l", newline=True)
    assert backend.read_gpio_pin_digital_state(pin) is False
    check_sent_data(serial, b"r", pin)

    # Append no received data - invalid
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_digital_state(pin)
    check_sent_data(serial, b"r", pin)

    serial.append_received_data(b"x", newline=True)  # invalid
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_digital_state(pin)
    check_sent_data(serial, b"r", pin)

    serial.check_all_received_data_consumed()


def test_backend_read_analogue() -> None:
    """Test that we can read the digital state of a pin."""
    backend = make_backend()
    serial = cast(RuggeduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    readings = [212, 535, 662, 385]
    for i, expected_reading in enumerate(readings):
        identifier = 14 + i
        serial.append_received_data(str(expected_reading).encode("utf-8"), newline=True)
        expected_voltage = (expected_reading / 1024.0) * 5.0
        measured_voltage = backend.read_gpio_pin_analogue_value(identifier)
        assert isclose(measured_voltage, expected_voltage)
        check_sent_data(serial, b"a", i)

    with pytest.raises(NotSupportedByHardwareError):
        backend.read_gpio_pin_analogue_value(ArduinoUno.FIRST_ANALOGUE_PIN + 6)  # invalid

    serial.check_all_received_data_consumed()


def test_backend_execute_string_command() -> None:
    """Test that we can execute custom commands."""

    class RuggeduinoSerialCustom(RuggeduinoSerial):
        """Like RuggeduinoSerial, but with a custom version string."""

        def respond_to_write(self, data: bytes) -> None:
            """Hook that can be overriden by subclasses to respond to sent data."""
            if data == b"v":
                version_line: bytes = b"SRcustom:" + self.firmware_version.encode("utf-8")
                self.append_received_data(version_line, newline=True)
            elif data == b"foo":
                self.append_received_data(data[::-1], newline=True)

    backend = make_backend(RuggeduinoSerialCustom)

    assert backend.execute_string_command("foo") == "oof"


def test_backend_execute_string_command_requires_unofficial_firmware() -> None:
    """Test that we need an unofficial firmware version to execute custom commands."""
    backend = make_backend()

    with pytest.raises(NotSupportedByHardwareError):
        backend.execute_string_command("foo")
