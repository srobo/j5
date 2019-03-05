"""Test the Hardware Enviroment."""

from j5.backends import Environment
from j5.backends.hardware import HardwareEnvironment


def test_hardware_environment():
    """Test that the Hardware Environment works."""
    assert type(HardwareEnvironment) is Environment

    assert HardwareEnvironment.name == "HardwareEnvironment"
