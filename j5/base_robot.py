"""A base class for robots."""

import socket

from j5.boards import Board


class UnableToObtainLock(OSError):
    """Unable to obtain lock."""

    pass


class BaseRobot:
    """A base robot."""

    def __new__(cls, *args, **kwargs) -> 'BaseRobot':  # type: ignore
        """
        Create a new instance of the class.

        :returns: Instance of a robot object.

        # noqa: DAR101
        """
        obj: BaseRobot = super().__new__(cls)
        obj._obtain_lock()
        return obj

    def make_safe(self) -> None:
        """Make this robot safe."""
        Board.make_all_safe()

    def _obtain_lock(self, lock_port: int = 10653) -> None:
        """
        Obtain a lock.

        This ensures that there can only be one instance of
        Robot at any time, which is a safety feature.

        :param lock_port: TCP port number to use for system-wide lock.
        :raises OSError: An error occured when the socket was created.
        :raises UnableToObtainLock: Could not obtain the lock on the port.
        """
        if not hasattr(self, '_lock'):

            self._lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self._lock.bind(('localhost', lock_port))
            except OSError:
                raise UnableToObtainLock(
                    "Unable to obtain lock. \
                    Are you trying to create more than one Robot object?",
                ) from None

            # We have no need to listen on the socket - we just bind to claim the address
            # and prevent another process using it.

        lock_details = self._lock.getsockname()
        if lock_details[1] != lock_port:
            raise OSError("Socket for lock is on the wrong port.")
