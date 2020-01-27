"""Test the abstract serial backend."""
# from typing import Optional, Set
#
# import pytest
# from serial import SerialException, SerialTimeoutException
#
# from j5.backends import CommunicationError
# from j5.backends.hardware.j5.serial import SerialHardwareBackend
# from j5.boards import Board
#
#
# class MockBrokenSerialHardwareBackend(SerialHardwareBackend):
#     """A SerialHardwareBackend with broken serial."""
#
#     @classmethod
#     def discover(cls) -> Set[Board]:
#         return set()
#
#     @property
#     def firmware_version(self) -> Optional[str]:
#         return None
#
#
# @handle_serial_error
# def my_function() -> None:
#     """A test function."""
#     assert True
#
#
# @handle_serial_error
# def raise_serial_timeout() -> None:
#     """A test function."""
#     raise SerialTimeoutException()
#
#
# @handle_serial_error
# def raise_serial_error() -> None:
#     """A test function."""
#     raise SerialException()
#
#
# def test_handle_serial_error() -> None:
#     """Test that the handle_serial_error_decorator behaves as expected."""
#     my_function()
#
#     with pytest.raises(CommunicationError):
#         raise_serial_timeout()
#
#     with pytest.raises(CommunicationError):
#         raise_serial_error()
