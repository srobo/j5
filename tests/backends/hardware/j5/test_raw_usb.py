"""Test the abstract Raw USB backend."""

import pytest
import usb

from j5.backends.hardware.j5.raw_usb import (
    ReadCommand,
    USBCommunicationError,
    WriteCommand,
)


def test_read_command() -> None:
    """Test that ReadCommand behaves as expected."""
    rc = ReadCommand(1, 2)

    assert type(rc) is ReadCommand
    assert type(rc.code) is int
    assert type(rc.data_len) is int
    assert rc.code == 1
    assert rc.data_len == 2


def test_write_command() -> None:
    """Test that WriteCommand behaves as expected."""
    wc = WriteCommand(1)

    assert type(wc) is WriteCommand
    assert type(wc.code) is int
    assert wc.code == 1


def test_usb_communication_error() -> None:
    """Test that USBCommunicationError works."""
    u = USBCommunicationError(usb.core.USBError("Test."))
    assert str(u) == "Test."
    assert issubclass(USBCommunicationError, Exception)
