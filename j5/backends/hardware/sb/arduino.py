"""SourceBots Arduino Hardware Implementation."""

from datetime import timedelta
from threading import Lock
from typing import Callable, List, Mapping, Optional, Set, Tuple, Type

from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import CommunicationError
from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.sb.arduino import SBArduinoBoard
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface
from j5.components.derived import UltrasoundInterface

USB_IDS: Set[Tuple[int, int]] = {
    (0x2341, 0x0043),  # Fake Uno
    (0x2a03, 0x0043),  # Fake Uno
    (0x1a86, 0x7523),  # Real Uno
}

FIRST_ANALOGUE_PIN = 14


def is_arduino_uno(port: ListPortInfo) -> bool:
    """Check if a ListPortInfo represents an Arduino Uno."""
    return (port.vid, port.pid) in USB_IDS


class DigitalPinData:
    """Contains data about a digital pin."""

    mode: GPIOPinMode
    state: bool

    def __init__(self, *, mode: GPIOPinMode, state: bool):
        self.mode = mode
        self.state = state


class SBArduinoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
    UltrasoundInterface,
    SerialHardwareBackend,
):
    """
    Hardware Backend for the Arduino Uno.

    Currently only for the SourceBots Arduino Firmware.
    """

    board = SBArduinoBoard

    @classmethod
    def discover(
            cls,
            comports: Callable = comports,
            serial_class: Type[Serial] = Serial,
    ) -> Set[Board]:
        """Discover all connected motor boards."""
        # Find all serial ports.
        ports: List[ListPortInfo] = comports()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(is_arduino_uno, ports):
            boards.add(
                SBArduinoBoard(
                    port.serial_number,
                    cls(port.device, serial_class),  # type: ignore
                ),
            )

        return boards

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
    ) -> None:
        super(SBArduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=115200,
            timeout=timedelta(milliseconds=1250),
        )

        self._lock = Lock()

        self._digital_pins: Mapping[int, DigitalPinData] = {
            i: DigitalPinData(mode=GPIOPinMode.DIGITAL_INPUT, state=False)
            for i in range(2, FIRST_ANALOGUE_PIN)
        }

        with self._lock:
            count = 0
            line = self.read_serial_line(empty=True)
            while len(line) == 0:
                line = self.read_serial_line(empty=True)
                count += 1
                if count > 25:
                    raise CommunicationError(
                        f"Arduino ({serial_port}) is not responding.",
                    )

            if line != "# Booted":
                raise CommunicationError("Arduino Boot Error.")

            self._version_line = self.read_serial_line()

        if self.firmware_version is not None:
            version_ids = tuple(map(int, self.firmware_version.split(".")))
        else:
            version_ids = (0, 0, 0)

        if version_ids < (2019, 6, 0):
            raise CommunicationError(
                f"Unexpected firmware version: {self.firmware_version},",
                f" expected at least: \"2019.6.0\".",
            )

        for pin_number in self._digital_pins.keys():
            self.set_gpio_pin_mode(pin_number, GPIOPinMode.DIGITAL_INPUT)

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line.split("v")[1]

    def _command(self, command: str, *params: str) -> List[str]:
        """Send a command to the board."""
        try:
            with self._lock:
                message = " ".join([command] + list(params)) + "\n"
                self._serial.write(message.encode("utf-8"))

                results: List[str] = []
                while True:
                    line = self.read_serial_line(empty=False)
                    code, param = line.split(None, 1)
                    if code == "+":
                        return results
                    elif code == "-":
                        raise CommunicationError(f"Arduino error: {param}")
                    elif code == ">":
                        results.append(param)
                    elif code == "#":
                        pass  # Ignore comment lines
                    else:
                        raise CommunicationError(
                            f"Arduino returned unrecognised response line: {line}",
                        )
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    def _update_digital_pin(self, identifier: int) -> None:
        if identifier >= FIRST_ANALOGUE_PIN:
            raise RuntimeError("Reached an unreachable statement.")
        pin = self._digital_pins[identifier]
        char: str
        if pin.mode == GPIOPinMode.DIGITAL_INPUT:
            char = "Z"
        elif pin.mode == GPIOPinMode.DIGITAL_INPUT_PULLUP:
            char = "P"
        elif pin.mode == GPIOPinMode.DIGITAL_OUTPUT:
            if pin.state:
                char = "H"
            else:
                char = "L"
        else:
            raise RuntimeError("Reached an unreachable statement.")
        self._command("W", str(identifier), char)

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the hardware mode of a GPIO pin."""
        digital_pin_modes = (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_OUTPUT,
        )
        if identifier < FIRST_ANALOGUE_PIN:
            # Digital pin
            if pin_mode in digital_pin_modes:
                self._digital_pins[identifier].mode = pin_mode
                self._update_digital_pin(identifier)
                return
        else:
            # Analogue pin
            if pin_mode is GPIOPinMode.ANALOGUE_INPUT:
                return
        raise NotSupportedByHardwareError(
            f"Arduino Uno does not support mode {pin_mode} on pin {identifier}",
        )

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            return self._digital_pins[identifier].mode
        else:
            return GPIOPinMode.ANALOGUE_INPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Write to the digital state of a GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to set the digital state.")
        self._digital_pins[identifier].state = state
        self._update_digital_pin(identifier)

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to read the digital state.")
        return self._digital_pins[identifier].state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode not in (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
        ):
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_*"
                             f"in order to read the digital state.")
        results = self._command("R", str(identifier))
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        if result == "H":
            return True
        elif result == "L":
            return False
        else:
            raise CommunicationError(f"Invalid response from Arduino: {result!r}")

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the analogue voltage of the GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Analogue functions not supported on digital pins",
            )
        if identifier >= FIRST_ANALOGUE_PIN + 4:
            raise NotSupportedByHardwareError(
                f"Arduino Uno firmware only supports analogue pins 0-3 (IDs 14-17)",
            )
        analogue_pin_num = identifier - 14
        results = self._command("A")
        for result in results:
            pin_name, reading = result.split(None, 1)
            if pin_name == f"a{analogue_pin_num}":
                voltage = (int(reading) / 1024.0) * 5.0
                return voltage
        raise CommunicationError(f"Invalid response from Arduino: {results!r}")

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        raise NotSupportedByHardwareError("SB Arduino does not have a DAC")

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        raise NotSupportedByHardwareError(
            "SB Arduino firmware does not implement PWM output",
        )

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13)")
        self.write_gpio_pin_digital_state(13, state)

    def get_ultrasound_pulse(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """
        Get a timedelta for the ultrasound time.

        Returns None if the sensor times out.
        """
        self._check_ultrasound_pins(trigger_pin_identifier, echo_pin_identifier)
        results = self._command("T", str(trigger_pin_identifier),
                                str(echo_pin_identifier))
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        microseconds = float(result)
        if microseconds == 0:
            # arduino pulseIn() returned 0 which indicates a timeout.
            return None
        else:
            return timedelta(microseconds=microseconds)

    def get_ultrasound_distance(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> Optional[float]:
        """Get a distance in metres."""
        self._check_ultrasound_pins(trigger_pin_identifier, echo_pin_identifier)
        results = self._command("U", str(trigger_pin_identifier),
                                str(echo_pin_identifier))
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        millimetres = float(result)
        if millimetres == 0:
            # arduino pulseIn() returned 0 which indicates a timeout.
            return None
        else:
            return millimetres / 1000.0

    def _check_ultrasound_pins(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> None:
        if trigger_pin_identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Ultrasound functions not supported on analogue pins",
            )
        if echo_pin_identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Ultrasound functions not supported on analogue pins",
            )

    def _update_ultrasound_pin_modes(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> None:
        # Ultrasound functions force the pins into particular modes.
        self._digital_pins[trigger_pin_identifier].mode = GPIOPinMode.DIGITAL_OUTPUT
        self._digital_pins[trigger_pin_identifier].state = False
        self._digital_pins[echo_pin_identifier].mode = GPIOPinMode.DIGITAL_INPUT
