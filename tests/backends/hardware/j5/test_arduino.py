"""Tests for the base Arduino hardware implementation."""
from datetime import timedelta
from math import pi
from typing import List, Optional, Set, Type

import pytest
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo
from tests.backends.hardware.j5.mock_serial import MockSerial

from j5.backends.hardware import NotSupportedByHardwareError
from j5.backends.hardware.j5.arduino import ArduinoHardwareBackend
from j5.boards import Board
from j5.boards.arduino import ArduinoUno
from j5.components import GPIOPinMode

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
        # TODO Write something to confirm that these have been called

    def _read_digital_pin(self, identifier: int) -> bool:
        """Read the value of a digital pin from the Arduino."""
        return True

    def _read_analogue_pin(self, identifier: int) -> float:
        """Read the value of an analogue pin from the Arduino."""
        return pi


def make_backend() -> MockArduinoBackend:
    """Instantiate a MockArduinoBackend with default arguments."""
    return MockArduinoBackend("COM0", MockSerial)  # type: ignore


def test_backend_default_timeout() -> None:
    """Test that a default timeout exists that is a timedelta."""
    assert isinstance(ArduinoHardwareBackend.DEFAULT_TIMEOUT, timedelta)


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


def make_port_info(vid: int, pid: int) -> ListPortInfo:
    """Make a ListPortInfo object from a USB vendor ID and product ID."""
    list_port_info = ListPortInfo("/dev/null")
    list_port_info.vid, list_port_info.pid = vid, pid
    return list_port_info


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

    assert backend.get_gpio_pin_mode(pin) is GPIOPinMode.DIGITAL_INPUT
    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_OUTPUT)
    assert backend.get_gpio_pin_mode(pin) is GPIOPinMode.DIGITAL_OUTPUT
    assert backend.get_gpio_pin_mode(EDGE_ANALOGUE_PIN) is GPIOPinMode.ANALOGUE_INPUT


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
            backend.set_gpio_pin_mode(pin, mode)
        else:
            with pytest.raises(NotSupportedByHardwareError):
                backend.set_gpio_pin_mode(pin, mode)


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

    backend.set_gpio_pin_mode(pin, GPIOPinMode.DIGITAL_INPUT)
    assert backend.read_gpio_pin_digital_state(pin) is True


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
    assert make_backend().read_gpio_pin_analogue_value(EDGE_ANALOGUE_PIN) is pi


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
    backend = make_backend()

    backend.set_gpio_pin_mode(13, GPIOPinMode.DIGITAL_OUTPUT)
    backend.set_led_state(0, True)
    assert backend.get_led_state(0) is True


def test_backend_nonzero_led_identifier() -> None:
    """Test that the only allowed LED identifier is 0."""
    backend = make_backend()

    backend.set_gpio_pin_mode(13, GPIOPinMode.DIGITAL_OUTPUT)
    with pytest.raises(ValueError):
        backend.get_led_state(1)
    with pytest.raises(ValueError):
        backend.set_led_state(1, True)
