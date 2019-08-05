"""Interface for board serial numbers."""

from abc import abstractmethod

from j5.components.component import Interface


class SerialNumberInterface(Interface):
    """An interface for retrieve a board's serial number."""

    @abstractmethod
    def get_serial_number(self) -> str:
        """Get the serial number."""
        raise NotImplementedError  # pragma: no cover
