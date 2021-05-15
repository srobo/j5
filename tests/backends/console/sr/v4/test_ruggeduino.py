"""Tests for the SR Ruggeduino console backend."""

import pytest

from j5.backends.console.sr.v4 import SRV4RuggeduinoConsoleBackend
from j5.boards.sr.v4 import Ruggeduino
from j5.components.gpio_pin import GPIOPinMode
from tests.backends.console.helpers import MockConsole


def test_backend_initialisation() -> None:
    """Test that we can initialise a Backend."""
    backend = SRV4RuggeduinoConsoleBackend("test")
    assert isinstance(backend, SRV4RuggeduinoConsoleBackend)

    assert len(backend._pins) == 18

    # Check all DIGITAL_OUTPUT
    assert all(pin.mode is GPIOPinMode.DIGITAL_OUTPUT for pin in backend._pins.values())

    # Check all False
    assert all(not pin.digital_state for pin in backend._pins.values())


def test_backend_discover() -> None:
    """
    Test that the backend can not discover boards.

    This backend does not support discovery.
    """
    boards = SRV4RuggeduinoConsoleBackend.discover()
    assert len(boards) == 1
    assert isinstance(list(boards)[0], Ruggeduino)


def test_backend_firmware_version() -> None:
    """Test that we can get the firmware version."""
    backend = SRV4RuggeduinoConsoleBackend("TestBoard")

    assert backend.firmware_version is None


def test_set_gpio_pin_mode() -> None:
    """Test that we can set the mode of a GPIO pin."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Set pin 10 to DIGITAL_OUTPUT"  # type: ignore
    backend.set_gpio_pin_mode(10, GPIOPinMode.DIGITAL_OUTPUT)

    backend._console.expects = "Set pin 2 to DIGITAL_INPUT"  # type: ignore
    backend.set_gpio_pin_mode(2, GPIOPinMode.DIGITAL_INPUT)

    backend._console.expects = "Set pin 8 to ANALOGUE_INPUT"  # type: ignore
    backend.set_gpio_pin_mode(8, GPIOPinMode.ANALOGUE_INPUT)


def test_get_gpio_pin_mode() -> None:
    """Test that we can get the mode of a GPIO Pin."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    assert backend.get_gpio_pin_mode(2) == GPIOPinMode.DIGITAL_OUTPUT

    backend._pins[5].mode = GPIOPinMode.DIGITAL_INPUT_PULLDOWN
    assert backend.get_gpio_pin_mode(5) == GPIOPinMode.DIGITAL_INPUT_PULLDOWN

    backend._pins[7].mode = GPIOPinMode.ANALOGUE_OUTPUT
    assert backend.get_gpio_pin_mode(7) == GPIOPinMode.ANALOGUE_OUTPUT


def test_write_gpio_pin_digital_state() -> None:
    """Test that we can write a digital state."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Set pin 10 state to True"  # type: ignore
    backend.write_gpio_pin_digital_state(10, True)

    backend._console.expects = "Set pin 15 state to False"  # type: ignore
    backend.write_gpio_pin_digital_state(15, False)


def test_write_gpio_pin_digital_state_bad_mode() -> None:
    """Test that we cannot write a digital state in the wrong mode."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._pins[4].mode = GPIOPinMode.DIGITAL_INPUT_PULLDOWN

    with pytest.raises(ValueError):
        backend.write_gpio_pin_digital_state(4, True)


def test_get_gpio_pin_digital_state() -> None:
    """Test that we can get a digital state."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._pins[10].digital_state = False
    assert not backend.get_gpio_pin_digital_state(10)

    backend._pins[10].digital_state = True
    assert backend.get_gpio_pin_digital_state(10)


def test_get_gpio_pin_digital_state_bad_mode() -> None:
    """Test that we cannot get a digital state in the wrong mode."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._pins[4].mode = GPIOPinMode.DIGITAL_INPUT_PULLDOWN

    with pytest.raises(ValueError):
        backend.get_gpio_pin_digital_state(4)


def test_read_gpio_pin_digital_state() -> None:
    """Test that we can read the digital state of a pin."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._pins[10].mode = GPIOPinMode.DIGITAL_INPUT
    backend._console.next_input = "True"  # type: ignore
    assert backend.read_gpio_pin_digital_state(10)


def test_read_gpio_pin_digital_state_bad_mode() -> None:
    """Test that we cannot read a digital state in the wrong mode."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "True"  # type: ignore

    with pytest.raises(ValueError):
        assert backend.read_gpio_pin_digital_state(10)


def test_read_gpio_pin_analogue_value() -> None:
    """Test that we can read an analogue value."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "4.3"  # type: ignore
    backend._pins[5].mode = GPIOPinMode.ANALOGUE_INPUT
    assert backend.read_gpio_pin_analogue_value(5) == 4.3


def test_read_gpio_pin_analogue_value_bad_mode() -> None:
    """Test that we cannot read an analogue value in the wrong mode."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "4.3"  # type: ignore
    with pytest.raises(ValueError):
        assert backend.read_gpio_pin_analogue_value(5) == 4.3


def test_write_gpio_pin_dac_value() -> None:
    """Test that this isn't implemented."""
    backend = SRV4RuggeduinoConsoleBackend("test")

    with pytest.raises(NotImplementedError):
        backend.write_gpio_pin_dac_value(10, 1.0)


def test_write_gpio_pin_pwm_value() -> None:
    """Test that this isn't implemented."""
    backend = SRV4RuggeduinoConsoleBackend("test")

    with pytest.raises(NotImplementedError):
        backend.write_gpio_pin_pwm_value(10, 1.0)


def test_get_led_state() -> None:
    """Test that we can get the LED state."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )
    assert not backend.get_led_state(0)

    backend._pins[13].digital_state = True
    assert backend.get_led_state(0)


def test_set_led_state() -> None:
    """Test that we can set the LED state."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Set pin 13 state to False"  # type: ignore
    backend.set_led_state(0, False)
    assert not backend.get_led_state(0)

    backend._console.expects = "Set pin 13 state to True"  # type: ignore
    backend.set_led_state(0, True)
    assert backend.get_led_state(0)


def test_that_led_is_pin_13() -> None:
    """Test that the LED has the same state as Pin 13."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )
    backend._console.expects = "Set pin 13 state to False"  # type: ignore
    backend.set_led_state(0, False)

    assert not backend.get_led_state(0)


def test_one_led() -> None:
    """Test that we can only control LED 0."""
    backend = SRV4RuggeduinoConsoleBackend("test")
    with pytest.raises(ValueError):
        backend.set_led_state(1, False)

    with pytest.raises(ValueError):
        backend.get_led_state(1)


def test_string_command() -> None:
    """Test that the string command component works."""
    backend = SRV4RuggeduinoConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "response"  # type: ignore
    assert backend.execute_string_command("bees") == "response"
