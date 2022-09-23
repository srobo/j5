"""Discovery-only backend for legacy and serial drivers for Power Board."""
from typing import Set

from j5.backends import Backend
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard

from .legacy import SRV4LegacyPowerBoardHardwareBackend
from .serial import SRV4SerialProtocolPowerBoardHardwareBackend


class SRV4PowerBoardHardwareBackend(Backend):
    """Discovery-only backend for legacy and serial drivers for Power Board."""

    board = PowerBoard
    discover_only = True

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        legacy_fw_boards = SRV4LegacyPowerBoardHardwareBackend.discover()
        serial_fw_boards = SRV4SerialProtocolPowerBoardHardwareBackend.discover()
        return legacy_fw_boards | serial_fw_boards
