"""Test the backend for the SR v4 Power Board serial protocol."""
import re
from datetime import timedelta
from typing import cast

import pytest
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo

from j5.backends.backend import CommunicationError
from j5.backends.hardware import (
    DeviceMissingSerialNumberError,
    NotSupportedByHardwareError,
)
from j5.backends.hardware.sr.v4.serial import (
    SRV4SerialProtocolPowerBoardHardwareBackend,
)
from j5.boards.sr.v4 import PowerBoard
from tests.backends.hardware.j5.mock_serial import MockSerial


class MockListPortInfo:
    """This class mocks the behaviour of serial.tools.ListPortInfo."""

    def __init__(
            self,
            device: str,
            serial_number: str | None,
            vid: int = 0x1bda,
            pid: int = 0x0010,
            manufacturer: str = "Student Robotics",
            product: str = "Power Board v4",
    ) -> None:
        self.device = device
        self.serial_number = serial_number
        self.vid = vid
        self.pid = pid
        self.manufacturer = manufacturer
        self.product = product

    def usb_info(self) -> str:
        """Get a string containing information about the device."""
        return "USB Information"


class MockPowerSerialBackend(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    @classmethod
    def get_comports(cls) -> list[MockListPortInfo]:  # type: ignore[override]
        """Get the comports."""
        return [
            MockListPortInfo("COM0", "SERIAL0"),  # Valid Power Board
            MockListPortInfo("COM1", "SERIAL1"),  # Valid Power Board
            MockListPortInfo("COM2", "SERIAL2", vid=0x302),  # Bad VID
            MockListPortInfo("COM3", "SERIAL3", pid=0x3002),  # Bad PID
            MockListPortInfo(
                "COM4", "SERIAL4", manufacturer="Acme Inc",
            ),  # Bad Manufacturer
            MockListPortInfo(
                "COM5", "SERIAL5", product="Not a Power Board",
            ),  # Bad Product
        ]

    def get_serial_class(self) -> type[Serial]:
        """Get the serial class."""
        return PowerSerial  # type: ignore


class MockPowerSerialBadSerialNumberBackend(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    @classmethod
    def get_comports(cls) -> list[ListPortInfo]:
        """Get the comports."""
        return [
            MockListPortInfo("COM0", None),  # type: ignore
        ]


class PowerSerial(MockSerial):
    """PowerSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 115200

    commands = {
        r'\*IDN\?\n': lambda: b'Student Robotics:PBv4B:srABC:4.4',
        r'\*STATUS\?\n': lambda: b'0,0,0,0,0,0,0:20:1',
        r'\*RESET\n': lambda: b'ACK',

        r'BTN:START:GET\?\n': lambda: b'0:0',

        r'OUT:(\d):SET:(0|1)\n': lambda port, state: b'ACK',
        r'OUT:(\d):GET\?\n': lambda port: b'1' if port == "0" else b'0',
        r'OUT:(\d):I\?\n': lambda port: str(int(port) * 1200).encode("ascii"),

        r'BATT:V\?': lambda: b'12400',
        r'BATT:I\?': lambda: b'6900',

        r'LED:RUN:SET:(0|1|F)': lambda v: b'ACK',
        r'LED:ERR:SET:(0|1|F)': lambda v: b'ACK',

        r'NOTE:(\d+):(\d+)': lambda pitch, duration: b'ACK',
    }

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        for regex, func in self.commands.items():
            match = re.match(regex, data.decode("ascii"))
            if match:
                response = func(*match.groups())  # type: ignore
                self.append_received_data(response, newline=True)
                return

        self.append_received_data(b'NACK:Unrecognised command: ' + data, newline=True)

    def check_data_sent_by_constructor(self) -> None:
        """Check that the backend constructor sent expected data to the serial port."""
        self.check_sent_data(
            b'*IDN?\n'  # Version Check
            b'*RESET\n',  # Reset the board
        )


class MockPowerSerialBackendAlwaysNACK(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    def get_serial_class(self) -> type[Serial]:
        """Get the serial class."""
        class PowerSerialAlwaysNACK(PowerSerial):
            """A serial port that always returns NACK."""

            commands = {
                r'\*IDN\?\n': lambda: b'Student Robotics:Power Board v4:srABC:4.4',
                r'\*STATUS\?\n': lambda: b'0,0,0,0,0,0,0:20:1',
                r'\*RESET\n': lambda: b'ACK',
            }
        return PowerSerialAlwaysNACK  # type: ignore


class MockPowerSerialBackendBadData(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    def get_serial_class(self) -> type[Serial]:
        """Get the serial class."""
        class PowerSerialBadData(PowerSerial):
            """A serial port that always returns bad data."""

            commands = {
                r'\*IDN\?\n': lambda: b'Student Robotics:PBv4B:srABC:4.4',
                r'\*STATUS\?\n': lambda: b'0,0,0,0,0,0,0:20:1',
                r'\*RESET\n': lambda: b'ACK',
                r'OUT:(\d):GET\?\n': lambda port: b'67',
                r'BTN:START:GET\?\n': lambda: b'54',
            }
        return PowerSerialBadData  # type: ignore


class TestSRV4SerialProtocolPowerBoardHardwareBackend:
    """Test the backend for the SR v4 Power Board serial protocol."""

    def test_backend_discover(self) -> None:
        """Test that we correctly discover the two valid boards."""
        found_boards = MockPowerSerialBackend.discover()
        assert len(found_boards) == 2
        assert all(type(board) is PowerBoard for board in found_boards)

        assert {board.serial_number for board in found_boards} == {"SERIAL0", "SERIAL1"}

    def test_backend_discover_missing_serial_number(self) -> None:
        """Test that we correctly handle power boards without a serial number."""
        with pytest.raises(DeviceMissingSerialNumberError) as e:
            MockPowerSerialBadSerialNumberBackend.discover()
        assert e.match(
            "Found power board-like device without serial number. "
            "The power board is likely to be damaged: USB Information",
        )

    def test_backend_resets_board(self) -> None:
        """Test that we reset the board when it is initialised."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()

    def test_get_power_output_enabled(self) -> None:
        """Test that we can fetch whether a power output is enabled."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert backend.get_power_output_enabled(0)
        serial.check_sent_data(b"OUT:0:GET?\n")
        assert not backend.get_power_output_enabled(1)
        serial.check_sent_data(b"OUT:1:GET?\n")

    def test_get_power_output_enabled_bad_data(self) -> None:
        """Test that we get a CommunicationError on a bad response."""
        backend = MockPowerSerialBackendBadData("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_power_output_enabled(0)
        e.match('Power Board returned an invalid response: 67')

    @pytest.mark.parametrize("identifier", [-1, 7])
    def test_get_power_output_enabled_bad_identifier(self, identifier: int) -> None:
        """Test that we get a CommunicationError on a bad response."""
        backend = MockPowerSerialBackendBadData("COM0")
        with pytest.raises(ValueError) as e:
            backend.get_power_output_enabled(identifier)
        e.match(f"{identifier} is not a valid power output identifier")

    def test_get_power_output_enabled_nack(self) -> None:
        """Test that we get a CommunicationError on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_power_output_enabled(0)
        e.match('Power Board returned an error: Unrecognised command')

    def test_set_power_output_enabled(self) -> None:
        """Test that we can change whether a power output is enabled."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        backend.set_power_output_enabled(0, True)
        serial.check_sent_data(b"OUT:0:SET:1\n")
        backend.set_power_output_enabled(0, False)
        serial.check_sent_data(b"OUT:0:SET:0\n")

    def test_set_power_output_enabled_nack(self) -> None:
        """Test that we get a communicationerror on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.set_power_output_enabled(0, True)
        e.match('Power Board returned an error: Unrecognised command')

    @pytest.mark.parametrize(
        "identifier",
        [-1, 7],
    )
    def test_set_power_output_enabled_bad_identifier(self, identifier: int) -> None:
        """Test that we correctly handle an out of range power output."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(ValueError) as e:
            backend.set_power_output_enabled(identifier, False)
        serial.check_sent_data(b"")
        assert e.match(
            f"{identifier} is not a valid power output identifier",
        )

    def test_get_power_output_current(self) -> None:
        """Test that we can fetch the current of a given power output."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert backend.get_power_output_current(1) == 1.2
        serial.check_sent_data(b"OUT:1:I?\n")

    def test_get_power_output_current_nack(self) -> None:
        """Test that we get a communicationerror on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError):
            backend.get_power_output_current(0)

    @pytest.mark.parametrize(
        "identifier",
        [-1, 7],
    )
    def test_get_power_output_current_bad_identifier(self, identifier: int) -> None:
        """Test that we correctly handle an out of range power output."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(ValueError) as e:
            backend.get_power_output_current(identifier)
        serial.check_sent_data(b"")
        assert e.match(
            f"{identifier} is not a valid power output identifier",
        )

    def test_buzz(self) -> None:
        """Test that we correctly handle buzzing the piezo."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        backend.buzz(0, timedelta(milliseconds=500), 440, False)
        serial.check_sent_data(b"NOTE:440:500\n")

    def test_buzz_bad_duration(self) -> None:
        """Test that we correctly handle upper duration limit."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(NotSupportedByHardwareError) as e:
            backend.buzz(0, timedelta(milliseconds=2 ** 31), 440, False)
        assert e.match(
            "Piezo duration must be in range of 0 - 2147483647ms",
        )

    def test_buzz_invalid_duration(self) -> None:
        """Test that we correctly handle lower duration limit."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(NotSupportedByHardwareError) as e:
            backend.buzz(0, timedelta(milliseconds=-1), 440, False)
        assert e.match(
            "Piezo duration must be in range of 0 - 2147483647ms.",
        )

    def test_buzz_bad_frequency(self) -> None:
        """Test that we correctly handle upper frequency limit."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(NotSupportedByHardwareError) as e:
            backend.buzz(0, timedelta(milliseconds=500), 10001, False)
        assert e.match(
            "Piezo frequency must be in range of 0 - 10kHz.",
        )

    def test_buzz_invalid_frequency(self) -> None:
        """Test that we correctly handle lower frequency limit."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(NotSupportedByHardwareError) as e:
            backend.buzz(0, timedelta(milliseconds=500), -1, False)
        assert e.match(
            "Piezo frequency must be in range of 0 - 10kHz.",
        )

    def test_buzz_bad_identifier(self) -> None:
        """Test that we get a ValueError if the buzzer ID is not 0."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.buzz(1, timedelta(milliseconds=500), 1, False)
        assert e.match(
            "Invalid piezo identifier 1; the only valid identifier is 0.",
        )

    def test_buzz_nack(self) -> None:
        """Test that we get a communicationerror on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.buzz(0, timedelta(milliseconds=500), 1, False)
        e.match('Power Board returned an error: Unrecognised command')

    def test_get_button_state(self) -> None:
        """Test that we can get the button state."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert not backend.get_button_state(0)
        serial.check_sent_data(b"BTN:START:GET?\n")

    def test_get_button_state_bad_identifier(self) -> None:
        """Test that we check the button identifier."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.get_button_state(1)
        assert e.match("Invalid button identifier 1; the only valid identifier is 0.")

    def test_get_button_state_nack(self) -> None:
        """Test that we get a communication error on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_button_state(0)
        e.match('Power Board returned an error: Unrecognised command')

    def test_get_button_state_bad_data(self) -> None:
        """Test that we get a CommunicationError on a bad response."""
        backend = MockPowerSerialBackendBadData("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_button_state(0)
        e.match('Power Board returned an invalid response: 54')

    def test_get_battery_sensor_voltage(self) -> None:
        """Test that we can fetch the battery sensor voltage."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert backend.get_battery_sensor_voltage(0) == 12.4
        serial.check_sent_data(b"BATT:V?\n")

    def test_get_battery_sensor_voltage_bad_nack(self) -> None:
        """Test that we get a communication error on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_battery_sensor_voltage(0)
        e.match('Power Board returned an error: Unrecognised command')

    def test_get_battery_sensor_voltage_bad_identifier(self) -> None:
        """Test that we handle a bad battery sensor identifier."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.get_battery_sensor_voltage(1)
        assert e.match(
            "Invalid battery sensor identifier 1; the only valid identifier is 0.",
        )

    def test_get_battery_sensor_current(self) -> None:
        """Test that we can fetch the battery sensor current."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert backend.get_battery_sensor_current(0) == 6.9
        serial.check_sent_data(b"BATT:I?\n")

    def test_get_battery_sensor_current_bad_nack(self) -> None:
        """Test that we get a communication error on NACK."""
        backend = MockPowerSerialBackendAlwaysNACK("COM0")
        with pytest.raises(CommunicationError) as e:
            backend.get_battery_sensor_current(0)
        e.match('Power Board returned an error: Unrecognised command')

    def test_get_battery_sensor_current_bad_identifier(self) -> None:
        """Test that we handle a bad battery sensor identifier."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.get_battery_sensor_current(1)
        assert e.match(
            "Invalid battery sensor identifier 1; the only valid identifier is 0.",
        )

    @pytest.mark.parametrize("identifier", [0, 1])
    def test_get_led_state_initial(self, identifier: int) -> None:
        """Test that all LEDs are off initially."""
        backend = MockPowerSerialBackend("COM0")
        assert not backend.get_led_state(identifier)

    def test_get_led_state(self) -> None:
        """Test that we can fetch the LED state."""
        backend = MockPowerSerialBackend("COM0")
        assert not backend.get_led_state(0)

        backend._led_states[0] = True
        assert backend.get_led_state(0)

    def test_get_led_state_bad_identifier(self) -> None:
        """Test that we can fetch the LED state."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.get_led_state(12)
        assert e.match(
            "Invalid LED identifier 12; the only valid identifiers are 0 and 1.",
        )

    def test_set_led_state_run(self) -> None:
        """Test that we can set the RUN LED state."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        backend.set_led_state(0, True)
        serial.check_sent_data(b"LED:RUN:SET:1\n")

    def test_set_led_state_err(self) -> None:
        """Test that we can set the RUN LED state."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        backend.set_led_state(1, True)
        serial.check_sent_data(b"LED:ERR:SET:1\n")

    def test_set_led_state_bad_identifier(self) -> None:
        """Test that we can fetch the LED state."""
        backend = MockPowerSerialBackend("COM0")
        with pytest.raises(ValueError) as e:
            backend.set_led_state(12, False)
        assert e.match(
            "Invalid LED identifier 12; the only valid identifiers are 0 and 1.",
        )
