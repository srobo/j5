"""Tests for the SourceBots Arduino hardware implementation."""

from datetime import timedelta
from math import isclose
from typing import List, Optional, cast

import pytest
from serial import SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.sb.arduino import SBArduinoHardwareBackend
from j5.boards.arduino import ArduinoUno
from j5.components import GPIOPinMode
from tests.backends.hardware.j5.mock_serial import MockSerial

# Pins on the digital-analogue border
EDGE_ANALOGUE_PIN = ArduinoUno.FIRST_ANALOGUE_PIN
EDGE_DIGITAL_PIN = EDGE_ANALOGUE_PIN - 1


class SBArduinoSerial(MockSerial):
    """SBArduinoSerial is the same as MockSerial, but includes expected received data."""

    expected_baudrate = 115200
    firmware_version = "2019.6.0"

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None,
                 ):
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
        )
        self.append_received_data(b"# Booted", newline=True)
        version_line = b"# SBDuino GPIO v" + self.firmware_version.encode("utf-8")
        self.append_received_data(version_line, newline=True)

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        self.append_received_data(b"+ OK", newline=True)

    def check_data_sent_by_constructor(self) -> None:
        """Check that the backend constructor sent expected data to the serial port."""
        self.check_sent_data(b"")


class SBArduinoSerialBootFail(MockSerial):
    """Like SBArduinoSerial, but sends unintelligible data on boot."""

    expected_baudrate = 115200

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None,
                 ):
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
        )
        self.append_received_data(b"wserzuhigfdiou", newline=True)


class SBArduinoSerialNoBoot(MockSerial):
    """Like MockSerial, but with a faster baudrate. Receives nothing on initialisation."""

    expected_baudrate = 115200


class SBArduinoSerialBadVersion(SBArduinoSerial):
    """Like SBArduinoSerial, but reports a malformed version number."""

    firmware_version = "2019.7"


class SBArduinoSerialOldVersion1(SBArduinoSerial):
    """Like SBArduinoSerial, but reports an older version number."""

    firmware_version = "2018.7.0"


class SBArduinoSerialOldVersion2(SBArduinoSerial):
    """Like SBArduinoSerial, but reports an older version number."""

    firmware_version = "2019.5.0"


class SBArduinoSerialNewVersion1(SBArduinoSerial):
    """Like SBArduinoSerial, but reports an newer version number."""

    firmware_version = "2019.6.1"


class SBArduinoSerialNewVersion2(SBArduinoSerial):
    """Like SBArduinoSerial, but reports an newer version number."""

    firmware_version = "2019.7.0"


class SBArduinoSerialNewVersion3(SBArduinoSerial):
    """Like SBArduinoSerial, but reports an newer version number."""

    firmware_version = "2020.1.0"


class SBArduinoSerialFailureResponse(SBArduinoSerial):
    """Like SBArduinoSerial, but returns a failure response rather than success."""

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        self.append_received_data(b"- Something went wrong", newline=True)


class SBArduinoSerialCommentResponse(SBArduinoSerial):
    """Like SBArduinoSerial, but returns a failure response rather than success."""

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        self.append_received_data(b"# Comment", newline=True)
        # super(SBArduinoSerialCommentResponse, self).respond_to_write(data)
        self.append_received_data(b"+ OK", newline=True)


class SBArduinoSerialErrorResponse(SBArduinoSerial):
    """Like SBArduinoSerial, but returns an unitelligible response rather than success."""

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        self.append_received_data(b"dxbuwae souiqeon", newline=True)


class SBArduinoSerialTimeout(SBArduinoSerial):
    """Like SBArduinoSerial, but times out when trying to write."""

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        raise SerialTimeoutException()


class SBArduinoSerialException(SBArduinoSerial):
    """Like SBArduinoSerial, but raises a SerialException when trying to write."""

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        raise SerialException()


def make_backend() -> SBArduinoHardwareBackend:
    """Instantiate an SBArduinoHardwareBackend  with some default arguments."""
    return SBArduinoHardwareBackend("COM0", SBArduinoSerial)  # type: ignore


def test_backend_initialisation() -> None:
    """Test that we can initialise an SBArduinoHardwareBackend."""
    backend = make_backend()
    assert backend.serial_port == "COM0"
    assert isinstance(backend._serial, SBArduinoSerial)
    assert all(
        pin.mode is GPIOPinMode.DIGITAL_INPUT for pin in backend._digital_pins.values()
    )
    assert all(pin.state is False for pin in backend._digital_pins.values())


def test_backend_initialisation_serial() -> None:
    """Test commands/responses are sent/received during initialisation."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    serial.check_all_received_data_consumed()

    with pytest.raises(CommunicationError):
        SBArduinoHardwareBackend("COM0", SBArduinoSerialBootFail)  # type: ignore
    with pytest.raises(CommunicationError):
        SBArduinoHardwareBackend("COM0", SBArduinoSerialNoBoot)  # type: ignore


def test_backend_version_check() -> None:
    """Test that an exception is raised if the arduino reports an unsupported version."""
    with pytest.raises(CommunicationError):
        SBArduinoHardwareBackend("COM0", SBArduinoSerialBadVersion)  # type: ignore
    with pytest.raises(CommunicationError):
        SBArduinoHardwareBackend("COM0", SBArduinoSerialOldVersion1)  # type: ignore
    with pytest.raises(CommunicationError):
        SBArduinoHardwareBackend("COM0", SBArduinoSerialOldVersion2)  # type: ignore
    SBArduinoHardwareBackend("COM0", SBArduinoSerialNewVersion1)  # type: ignore
    SBArduinoHardwareBackend("COM0", SBArduinoSerialNewVersion2)  # type: ignore
    SBArduinoHardwareBackend("COM0", SBArduinoSerialNewVersion3)  # type: ignore


def test_backend_firmware_version() -> None:
    """Test that the firmware version is parsed correctly."""
    backend = make_backend()
    assert backend.firmware_version == SBArduinoSerial.firmware_version


def check_for_communication_error(backend: SBArduinoHardwareBackend) -> None:
    """Check that performing an operation on the backend raises a CommunicationError."""
    with pytest.raises(CommunicationError):
        backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)


def test_backend_handles_failure() -> None:
    """Test that an exception is raised when a failure response is received."""
    check_for_communication_error(SBArduinoHardwareBackend(
        "COM0",
        SBArduinoSerialFailureResponse,  # type: ignore
    ))


def test_backend_handles_unrecognised_response() -> None:
    """Test that an exception is raised when an unrecognised response is received."""
    check_for_communication_error(SBArduinoHardwareBackend(
        "COM0",
        SBArduinoSerialErrorResponse,  # type: ignore
    ))


def test_backend_handles_comment_response() -> None:
    """Test that comments in the Arduino's response are ignored."""
    backends: List[SBArduinoHardwareBackend] = [
        make_backend(),  # Normal
        SBArduinoHardwareBackend(  # Comment
            "COM0",
            SBArduinoSerialCommentResponse,  # type: ignore
        ),
    ]
    results: List[bool] = []
    for backend in backends:
        cast(SBArduinoSerial, backend._serial).append_received_data(b"> H", newline=True)
        results.append(backend.read_gpio_pin_digital_state(2))

    assert results[0] is results[1]


def test_backend_handles_serial_exeption() -> None:
    """Test that an exception is raised when a SerialException happens."""
    check_for_communication_error(SBArduinoHardwareBackend(
        "COM0",
        SBArduinoSerialTimeout,  # type: ignore
    ))
    check_for_communication_error(SBArduinoHardwareBackend(
        "COM0",
        SBArduinoSerialException,  # type: ignore
    ))


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


def test_backend_write_digital_state() -> None:
    """Test that we can write the digital state of a pin."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    # This should put the pin into the most recent (or default) output state.
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_OUTPUT)
    serial.check_sent_data(b"W 2 L\n")
    backend.write_gpio_pin_digital_state(2, True)
    serial.check_sent_data(b"W 2 H\n")
    backend.write_gpio_pin_digital_state(2, False)
    serial.check_sent_data(b"W 2 L\n")
    serial.check_all_received_data_consumed()


def test_backend_digital_state_persists() -> None:
    """Test switching to a different mode and then back to output."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_OUTPUT)
    serial.check_sent_data(b"W 2 L\n")
    backend.write_gpio_pin_digital_state(2, True)
    serial.check_sent_data(b"W 2 H\n")
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)
    serial.check_sent_data(b"W 2 Z\n")
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_OUTPUT)
    serial.check_sent_data(b"W 2 H\n")
    backend.write_gpio_pin_digital_state(2, False)
    serial.check_sent_data(b"W 2 L\n")
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)
    serial.check_sent_data(b"W 2 Z\n")
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_OUTPUT)
    serial.check_sent_data(b"W 2 L\n")
    serial.check_all_received_data_consumed()


def test_backend_input_modes() -> None:
    """Check that the correct commands are send when setting pins to input modes."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)
    serial.check_sent_data(b"W 2 Z\n")
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT_PULLUP)
    serial.check_sent_data(b"W 2 P\n")
    with pytest.raises(NotSupportedByHardwareError):
        backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT_PULLDOWN)
    serial.check_all_received_data_consumed()


def test_backend_read_digital_state() -> None:
    """Test that we can read the digital state of a pin."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)
    serial.check_sent_data(b"W 2 Z\n")

    serial.append_received_data(b"> H", newline=True)
    assert backend.read_gpio_pin_digital_state(2) is True
    serial.check_sent_data(b"R 2\n")

    serial.append_received_data(b"> L", newline=True)
    assert backend.read_gpio_pin_digital_state(2) is False
    serial.check_sent_data(b"R 2\n")

    # Append no received data - invalid
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_digital_state(2)
    serial.check_sent_data(b"R 2\n")

    serial.append_received_data(b"> X", newline=True)  # invalid
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_digital_state(2)
    serial.check_sent_data(b"R 2\n")

    serial.check_all_received_data_consumed()


def test_backend_read_analogue() -> None:
    """Test that we can read the digital state of a pin."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    readings = [212, 535, 662, 385]
    for i, expected_reading in enumerate(readings):
        # "read analogue" command reads all four pins at once.
        identifier = 14 + i
        for j, reading in enumerate(readings):
            serial.append_received_data(f"> a{j} {reading}".encode("utf-8"), newline=True)
        expected_voltage = (expected_reading / 1024.0) * 5.0
        measured_voltage = backend.read_gpio_pin_analogue_value(identifier)
        assert isclose(measured_voltage, expected_voltage)
        serial.check_sent_data(b"A\n")

    with pytest.raises(NotSupportedByHardwareError):
        backend.read_gpio_pin_analogue_value(ArduinoUno.FIRST_ANALOGUE_PIN + 4)  # invalid
    # Append no received results
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_analogue_value(ArduinoUno.FIRST_ANALOGUE_PIN)
    # Append an invalid received result
    serial.append_received_data(b"> a_cdwenh 583")
    with pytest.raises(CommunicationError):
        backend.read_gpio_pin_analogue_value(ArduinoUno.FIRST_ANALOGUE_PIN)

    serial.check_all_received_data_consumed()


def test_servo_read() -> None:
    """Test that we can read the position of the servo."""
    backend = make_backend()
    assert backend.get_servo_position(0) is None

    # Override the state
    backend._servo_states[4] = 0.8
    assert backend.get_servo_position(4) == 0.8


def test_servo_write() -> None:
    """Test that we can set the position of the servo."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.set_servo_position(3, 0)
    serial.check_sent_data(b"S 3 350\n")

    backend.set_servo_position(4, 0)
    serial.check_sent_data(b"S 4 350\n")

    backend.set_servo_position(4, -1)
    serial.check_sent_data(b"S 4 150\n")

    backend.set_servo_position(4, 1)
    serial.check_sent_data(b"S 4 550\n")

    backend.set_servo_position(3, None)
    serial.check_sent_data(b"S 3 0\n")

    serial.check_all_received_data_consumed()


def test_servo_set_out_of_range() -> None:
    """Test that we raise an error out of servo range."""
    backend = make_backend()

    with pytest.raises(ValueError):
        backend.set_servo_position(1, 2)

    with pytest.raises(ValueError):
        backend.set_servo_position(1, -2)


def test_ultrasound_pulse() -> None:
    """Test that we can read an ultrasound pulse time."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 2345\n")
    duration = backend.get_ultrasound_pulse(3, 4)
    serial.check_sent_data(b"T 3 4\n")
    assert duration == timedelta(microseconds=2345)

    # Check backend updated its view of what modes the pins are in now.
    assert backend.get_gpio_pin_mode(3) is GPIOPinMode.DIGITAL_OUTPUT
    assert backend.get_gpio_pin_digital_state(3) is False
    assert backend.get_gpio_pin_mode(4) is GPIOPinMode.DIGITAL_INPUT

    # Receive no results - invalid
    with pytest.raises(CommunicationError):
        backend.get_ultrasound_pulse(3, 4)
    serial.check_sent_data(b"T 3 4\n")

    serial.check_all_received_data_consumed()


def test_ultrasound_pulse_on_same_pin() -> None:
    """Test same pin for trigger and echo."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 2345\n")
    duration = backend.get_ultrasound_pulse(3, 3)
    serial.check_sent_data(b"T 3 3\n")
    assert duration == timedelta(microseconds=2345)

    # Check backend updated its view of what modes the pins are in now.
    assert backend.get_gpio_pin_mode(3) is GPIOPinMode.DIGITAL_INPUT

    serial.check_all_received_data_consumed()


def test_ultrasound_pulse_timeout() -> None:
    """Test that None is returned upon a timeout occurring."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 0\n")
    duration = backend.get_ultrasound_pulse(3, 4)
    serial.check_sent_data(b"T 3 4\n")
    assert duration is None

    serial.check_all_received_data_consumed()


def test_ultrasound_pulse_requires_digital_pins() -> None:
    """Test that an exception is raised if the trigger or echo pins are analogue."""
    backend = make_backend()

    with pytest.raises(NotSupportedByHardwareError):
        backend.get_ultrasound_pulse(EDGE_ANALOGUE_PIN, 2)
    with pytest.raises(NotSupportedByHardwareError):
        backend.get_ultrasound_pulse(2, EDGE_ANALOGUE_PIN)


def test_ultrasound_distance() -> None:
    """Test that we can read an ultrasound distance."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 1230\n")
    metres = backend.get_ultrasound_distance(3, 4)
    serial.check_sent_data(b"U 3 4\n")
    assert metres is not None
    assert isclose(metres, 1.23)

    # Check backend updated its view of what modes the pins are in now.
    assert backend.get_gpio_pin_mode(3) is GPIOPinMode.DIGITAL_OUTPUT
    assert backend.get_gpio_pin_digital_state(3) is False
    assert backend.get_gpio_pin_mode(4) is GPIOPinMode.DIGITAL_INPUT

    # Receive no results - invalid
    with pytest.raises(CommunicationError):
        backend.get_ultrasound_distance(3, 4)
    serial.check_sent_data(b"U 3 4\n")

    serial.check_all_received_data_consumed()


def test_ultrasound_distance_on_same_pin() -> None:
    """Test same pin for trigger and echo."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 1230\n")
    metres = backend.get_ultrasound_distance(3, 3)
    serial.check_sent_data(b"U 3 3\n")
    assert metres is not None
    assert isclose(metres, 1.23)

    # Check backend updated its view of what modes the pins are in now.
    assert backend.get_gpio_pin_mode(3) is GPIOPinMode.DIGITAL_INPUT

    serial.check_all_received_data_consumed()


def test_ultrasound_distance_timeout() -> None:
    """Test that None is returned upon a timeout occurring."""
    backend = make_backend()
    serial = cast(SBArduinoSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    serial.append_received_data(b"> 0\n")
    metres = backend.get_ultrasound_distance(3, 4)
    serial.check_sent_data(b"U 3 4\n")
    assert metres is None

    serial.check_all_received_data_consumed()


def test_ultrasound_distance_requires_digital_pins() -> None:
    """Test that an exception is raised if the trigger or echo pins are analogue."""
    backend = make_backend()

    with pytest.raises(NotSupportedByHardwareError):
        backend.get_ultrasound_distance(EDGE_ANALOGUE_PIN, 2)
    with pytest.raises(NotSupportedByHardwareError):
        backend.get_ultrasound_distance(2, EDGE_ANALOGUE_PIN)
