"""Classes for Battery Sensing Components."""

from abc import abstractmethod
from typing import Type

from j5.components.component import Component, Interface


class BatterySensorInterface(Interface):
    """An interface containing the methods required to read data from a BatterySensor."""

    @abstractmethod
    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """
        Get the voltage of a battery sensor.

        :param identifier: Identifier of battery sensor.
        :returns: voltage measured by the sensor.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_battery_sensor_current(self, identifier: int) -> float:
        """
        Get the current of a battery sensor.

        :param identifier: Identifier of battery sensor.
        :returns: current measured by the sensor.
        """
        raise NotImplementedError  # pragma: no cover


class BatterySensor(Component):
    """A sensor capable of monitoring a battery."""

    def __init__(
        self, identifier: int, backend: BatterySensorInterface,
    ) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[BatterySensorInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return BatterySensorInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    @property
    def voltage(self) -> float:
        """
        Get the voltage reported by the battery sensor.

        :returns: voltage measured by the sensor.
        """
        return self._backend.get_battery_sensor_voltage(self._identifier)

    @property
    def current(self) -> float:
        """
        Get the current of the battery sensor.

        :returns: current measured by the sensor.
        """
        return self._backend.get_battery_sensor_current(self._identifier)
