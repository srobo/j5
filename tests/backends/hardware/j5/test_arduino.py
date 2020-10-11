"""Tests for the base Arduino hardware implementation."""

from datetime import timedelta
from math import pi
from typing import List, Optional, Set, Tuple, Type, cast

import pytest
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo

from j5.backends.hardware import NotSupportedByHardwareError
from j5.backends.hardware.j5.arduino import ArduinoHardwareBackend
from j5.boards import Board
from j5.boards.arduino import ArduinoUno
from j5.components import GPIOPinMode
from tests.backends.hardware.j5.mock_serial import MockSerial

# Pins on the digital-analogue border
EDGE_ANALOGUE_PIN = ArduinoUno.FIRST_ANALOGUE_PIN
EDGE_DIGITAL_PIN = EDGE_ANALOGUE_PIN - 1


class MockArduinoBackend(ArduinoHardwareBackend):
    """A simple backend overriding ArduinoHardwareBackend's abstract methods."""

    board = ArduinoUno

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
            baud: int = 9600,
            timeout: timedelta = ArduinoHardwareBackend.DEFAULT_TIMEOUT,
    ) -> None:
        super(MockArduinoBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=baud,
            timeout=timeout,
        )

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    def _update_digital_pin(self, identifier: int) -> None:
        """Write the stored value of a digital pin to the Arduino."""
        self._serial.write(update_digital_pin_command(
            identifier,
            self._digital_pins[identifier].mode,
            self._digital_pins[identifier].state,
        ))

    def _read_digital_pin(self, identifier: int) -> bool:
        """Read the value of a digital pin from the Arduino."""
        message, result = read_digital_pin_command(identifier)
        self._serial.write(message)
        return result

    def _read_analogue_pin(self, identifier: int) -> float:
        """Read the value of an analogue pin from the Arduino."""
        message, result = read_analogue_pin_command(identifier)
        self._serial.write(message)
        return result


def make_backend() -> MockArduinoBackend:
    """Instantiate a MockArduinoBackend with some default arguments."""
    return MockArduinoBackend("COM0", MockSerial)  # type: ignore


def update_digital_pin_command(identifier: int, mode: GPIOPinMode, state: bool) -> bytes:
    """Generate a pin update command to send to the mock arduino board."""
    if mode in {GPIOPinMode.ANALOGUE_INPUT, GPIOPinMode.ANALOGUE_OUTPUT}:
        return b""

    return "_".join([
        "update",
        str(identifier),
        mode.name,
        str(state),
    ]).encode("utf-8")


def read_digital_pin_command(identifier: int) -> Tuple[bytes, bool]:
    """Generate a digital pin read command to send to the mock arduino board."""
    result: bool = identifier % 2 == 0
    return (
        "_".join([
            "readdigital",
            str(identifier),
            str(result),
        ]).encode("utf-8"),
        result,
    )


def read_analogue_pin_command(identifier: int) -> Tuple[bytes, float]:
    """Generate an analogue pin read command to send to the mock arduino board."""
    result: int = identifier
    return (
        "_".join([
            "readanalogue",
            str(identifier),
            str(result),
        ]).encode("utf-8"),
        float(result),
    )


def test_backend_default_timeout() -> None:
    """Test that a default timeout exists that is a timedelta."""
    assert isinstance(ArduinoHardwareBackend.DEFAULT_TIMEOUT, timedelta)


def make_port_info(vid: int, pid: int) -> ListPortInfo:
    """Make a ListPortInfo object from a USB vendor ID and product ID."""
    list_port_info = ListPortInfo("/dev/null")
    list_port_info.vid, list_port_info.pid = vid, pid
    return list_port_info


def test_backend_is_arduino() -> None:
    """Test that the USB IDs listed are recognised as Arduinos."""
    assert len(ArduinoHardwareBackend.USB_IDS) > 0
    assert all(
        ArduinoHardwareBackend.is_arduino(make_port_info(vid, pid))
        for vid, pid in ArduinoHardwareBackend.USB_IDS
    )


def test_backend_discover() -> None:
    """Test that we can discover Arduinos and only Arduinos."""
    arduino_ports: List[ListPortInfo] = [
        make_port_info(vid, pid)
        for vid, pid in ArduinoHardwareBackend.USB_IDS
    ]
    other_ports: List[ListPortInfo] = [
        make_port_info(vid, pid)
        for vid, pid in [
            (0x1e7d, 0x307a),  # Keyboard
            (0x1bda, 0x0010),  # Power board
            (0x0781, 0x5581),  # USB flash drive
        ]
    ]

    def discover_arduinos(ports: List[ListPortInfo]) -> Set[Board]:
        return MockArduinoBackend.discover(
            comports=lambda: ports,
            serial_class=MockSerial,  # type: ignore
        )

    # Find nothing
    assert discover_arduinos([]) == set()
    # Only find other devices
    assert discover_arduinos(other_ports) == set()
    # Only find one Arduino
    assert len(discover_arduinos([arduino_ports[0]])) == 1
    # Find one Arduino in a mixture
    assert len(discover_arduinos(other_ports + [arduino_ports[0]])) == 1
    # Find lots of Arduinos
    assert len(discover_arduinos(arduino_ports)) == len(arduino_ports)
    # Find lots of Arduinos in a mixture
    assert len(discover_arduinos(other_ports + arduino_ports)) == len(arduino_ports)
    # Make sure they're all Arduinos
    assert all(
        isinstance(board, MockArduinoBackend.board)
        for board in discover_arduinos(other_ports + arduino_ports)
    )


def test_backend_initialisation() -> None:
    """Test that we can initialise an ArduinoHardwareBackend."""
    backend = make_backend()
    assert backend.serial_port == "COM0"
    assert isinstance(backend._serial, MockSerial)
    assert all(
        pin.mode is GPIOPinMode.DIGITAL_INPUT for pin in backend._digital_pins.values()
    )
    assert all(pin.state is False for pin in backend._digital_pins.values())


def test_backend_get_set_pin_mode() -> None:
    """Test that we can get and set pin modes."""
    pin = EDGE_DIGITAL_PIN
    backend = make_backend()

    assert backend.get_gpio_pin_mode(EDGE_ANALOGUE_PIN) is GPIOPinMode.ANALOGUE_INPUT
    assert backend.get_gpio_pin_mode(pin) is GPIOPinMode.DIGITAL_INPUT
    serial = cast(MockSerial, backend._serial)
    mode = GPIOPinMode.DIGITAL_OUTPUT
    backend.set_gpio_pin_mode(pin, mode)
    serial.check_sent_data(update_digital_pin_command(pin, mode, False))
    assert backend.get_gpio_pin_mode(pin) is mode


def test_backend_digital_pin_modes() -> None:
    """Test that only certain modes are valid on digital pins."""
    legal_modes: Set[GPIOPinMode] = {
        GPIOPinMode.DIGITAL_INPUT,
        GPIOPinMode.DIGITAL_INPUT_PULLUP,
        GPIOPinMode.DIGITAL_OUTPUT,
    }
    check_pin_modes(make_backend(), EDGE_DIGITAL_PIN, legal_modes)


def test_backend_analogue_pin_modes() -> None:
    """Test that only certain modes are valid on digital pins."""
    legal_modes: Set[GPIOPinMode] = {
        GPIOPinMode.ANALOGUE_INPUT,
    }
    check_pin_modes(make_backend(), EDGE_ANALOGUE_PIN, legal_modes)


def check_pin_modes(
        backend: ArduinoHardwareBackend,
        pin: ArduinoUno.PinNumber,
        legal_modes: Set[GPIOPinMode],
) -> None:
    """Check that a set of modes is supported on a backend for a pin."""
    for mode in GPIOPinMode:
        if mode in legal_modes:
            serial = cast(MockSerial, backend._serial)
            backend.set_gpio_pin_mode(pin, mode)
            serial.check_sent_data(update_digital_pin_command(pin, mode, False))
        else:
            with pytest.raises(NotSupportedByHardwareError):
                backend.set_gpio_pin_mode(pin, mode)


def test_backend_write_digital_state() -> None:
    """Test that we can write a new digital state to a pin."""
    pin = 2
    mode = GPIOPinMode.DIGITAL_OUTPUT
    backend = make_backend()
    serial = cast(MockSerial, backend._serial)

    backend.set_gpio_pin_mode(pin, mode)
    serial.check_sent_data(update_digital_pin_command(pin, mode, False))
    backend.write_gpio_pin_digital_state(pin, True)
    assert backend.get_gpio_pin_digital_state(pin) is True
    serial.check_sent_data(update_digital_pin_command(pin, mode, True))


def test_backend_write_digital_state_requires_pin_mode() -> None:
    """Check that pin must be in DIGITAL_OUTPUT mode for write digital state to work."""
    pin = 2
    backend = make_backend()

    assert backend.get_gpio_pin_mode(pin) is not GPIOPinMode.DIGITAL_OUTPUT
    with pytest.raises(ValueError):
        backend.write_gpio_pin_digital_state(pin, True)


def test_backend_write_digital_state_requires_digital_pin() -> None:
    """Check that pins 14-19 are not supported by write digital state."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().write_gpio_pin_digital_state(EDGE_ANALOGUE_PIN, True)


def test_backend_get_digital_state() -> None:
    """Test that we can recall the digital state of a pin."""
    pin = 2
    backend = make_backend()

    # This should put the pin into the most recent (or default) output state.
    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    assert backend.get_gpio_pin_digital_state(pin) is False
    backend.write_gpio_pin_digital_state(pin, True)
    assert backend.get_gpio_pin_digital_state(pin) is True
    backend.write_gpio_pin_digital_state(pin, False)
    assert backend.get_gpio_pin_digital_state(pin) is False


def test_backend_get_digital_state_requires_pin_mode() -> None:
    """Check that pin must not be in DIGITAL_OUTPUT mode for get digital state to work."""
    pin = 2
    backend = make_backend()

    assert backend.get_gpio_pin_mode(pin) is not GPIOPinMode.DIGITAL_OUTPUT
    with pytest.raises(ValueError):
        backend.get_gpio_pin_digital_state(pin)


def test_backend_get_digital_state_requires_digital_pin() -> None:
    """Check that pins 14-19 are not supported by get digital state."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().get_gpio_pin_digital_state(EDGE_ANALOGUE_PIN)


def test_backend_read_digital_state() -> None:
    """Test that we can read the digital state of a pin."""
    pin = 2
    backend = make_backend()
    serial = cast(MockSerial, backend._serial)

    assert backend.get_gpio_pin_mode(pin) is GPIOPinMode.DIGITAL_INPUT
    expected_message, expected_result = read_digital_pin_command(pin)
    assert backend.read_gpio_pin_digital_state(pin) is expected_result
    serial.check_sent_data(expected_message)


def test_backend_read_digital_state_requires_pin_mode() -> None:
    """Check that pin must be in DIGITAL_INPUT* mode for read digital state to work."""
    pin = 2
    backend = make_backend()

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    assert backend.get_gpio_pin_mode(pin) is not GPIOPinMode.DIGITAL_INPUT
    with pytest.raises(ValueError):
        backend.read_gpio_pin_digital_state(pin)


def test_backend_read_digital_state_requires_digital_pin() -> None:
    """Check that pins 14-19 are not supported by read digital state."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().read_gpio_pin_digital_state(EDGE_ANALOGUE_PIN)


def test_backend_read_analogue() -> None:
    """Test that we can read the digital state of a pin."""
    pin = EDGE_ANALOGUE_PIN
    backend = make_backend()
    serial = cast(MockSerial, backend._serial)

    expected_message, expected_result = read_analogue_pin_command(pin)
    assert backend.read_gpio_pin_analogue_value(pin) == expected_result
    serial.check_sent_data(expected_message)


def test_backend_read_analogue_requires_analogue_pin() -> None:
    """Check that pins 2-13 are not supported by read analogue."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().read_gpio_pin_analogue_value(EDGE_DIGITAL_PIN)


def test_backend_write_analogue_not_supported() -> None:
    """Test that writing an analogue value to a pin is unsupported."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().write_gpio_pin_dac_value(2, pi)


def test_backend_write_pwm_not_supported() -> None:
    """Test that writing a PWM value to a pin is unsupported."""
    with pytest.raises(NotSupportedByHardwareError):
        make_backend().write_gpio_pin_pwm_value(3, 0.3)


def test_backend_get_set_led_state() -> None:
    """Test that we can recall and set the state of the LED."""
    pin = 13
    mode = GPIOPinMode.DIGITAL_OUTPUT
    backend = make_backend()
    serial = cast(MockSerial, backend._serial)

    backend.set_gpio_pin_mode(pin, mode)
    serial.check_sent_data(update_digital_pin_command(pin, mode, False))
    backend.set_led_state(0, True)
    serial.check_sent_data(update_digital_pin_command(pin, mode, True))
    assert backend.get_led_state(0) is True


def test_backend_nonzero_led_identifier() -> None:
    """Test that the only allowed LED identifier is 0."""
    backend = make_backend()

    backend.set_gpio_pin_mode(13, GPIOPinMode.DIGITAL_OUTPUT)
    with pytest.raises(ValueError):
        backend.get_led_state(1)
    with pytest.raises(ValueError):
        backend.set_led_state(1, True)
