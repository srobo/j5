"""Classes for GPIO Pins."""

from abc import abstractmethod
from enum import IntEnum
from typing import Set, Type, Union

from j5.components.component import (
    Component,
    DerivedComponent,
    Interface,
    NotSupportedByComponentError,
)


class BadGPIOPinModeError(Exception):
    """The pin is not in the correct mode."""

    pass


class GPIOPinMode(IntEnum):
    """Hardware modes that a GPIO pin can be set to."""

    DIGITAL_INPUT = 0  #: The digital state of the pin can be read
    DIGITAL_INPUT_PULLUP = 1  #: Same as DIGITAL_INPUT but internal pull-up is enabled
    DIGITAL_INPUT_PULLDOWN = 2  #: Same as DIGITAL_INPUT but internal pull-down is enabled
    DIGITAL_OUTPUT = 3  #: The digital state of the pin can be set.

    ANALOGUE_INPUT = 4  #: The analogue voltage of the pin can be read.
    ANALOGUE_OUTPUT = 5  #: The analogue voltage of the pin can be set using a DAC.

    PWM_OUTPUT = 6  #: A PWM output signal can be created on the pin.


FirmwareMode = Type[DerivedComponent]

PinMode = Union[FirmwareMode, GPIOPinMode]


class GPIOPinInterface(Interface):
    """An interface containing the methods required for a GPIO Pin."""

    @abstractmethod
    def set_gpio_pin_mode(self,
                          identifier: int,
                          pin_mode: GPIOPinMode,
                          ) -> None:
        """Set the hardware mode of a GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def write_gpio_pin_digital_state(self,
                                     identifier: int,
                                     state: bool,
                                     ) -> None:
        """Write to the digital state of a GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the scaled analogue value of the GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def write_gpio_pin_dac_value(
            self,
            identifier: int,
            scaled_value: float,
    ) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def write_gpio_pin_pwm_value(
            self,
            identifier: int,
            duty_cycle: float,
    ) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        raise NotImplementedError  # pragma: nocover


class GPIOPin(Component):
    """A GPIO Pin."""

    DEFAULT_HW_MODE: Set[GPIOPinMode] = {GPIOPinMode.DIGITAL_OUTPUT}
    DEFAULT_FW_MODE: Set[FirmwareMode] = set()

    def __init__(
            self,
            identifier: int,
            backend: GPIOPinInterface,
            *,
            initial_mode: PinMode,
            hardware_modes: Set[GPIOPinMode] = DEFAULT_HW_MODE,
            firmware_modes: Set[FirmwareMode] = DEFAULT_FW_MODE,
    ) -> None:
        self._backend = backend
        self._identifier = identifier
        self._supported_modes = hardware_modes
        self._firmware_modes = firmware_modes

        if len(hardware_modes) < 1:
            raise ValueError("A GPIO pin must support at least one hardware mode.")

        self.mode = initial_mode

    @staticmethod
    def interface_class() -> Type[GPIOPinInterface]:
        """Get the interface class that is required to use this component."""
        return GPIOPinInterface

    def _require_pin_modes(self, pin_modes: Set[PinMode]) -> None:
        """Ensure that this pin is in the specified hardware mode."""
        if self.mode not in pin_modes and not len(pin_modes) == 0:
            raise BadGPIOPinModeError(
                f"Pin {self._identifier} needs to be in one of {pin_modes}",
            )

    @property
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        return self._identifier

    @property
    def mode(self) -> PinMode:
        """Get the mode of this pin."""
        return self._backend.get_gpio_pin_mode(self._identifier)

    @mode.setter
    def mode(self, pin_mode: PinMode) -> None:
        """Set the mode of this pin."""
        if pin_mode not in self._supported_modes | self._firmware_modes:
            raise NotSupportedByComponentError(
                f"Pin {self._identifier} does not support {str(pin_mode)}.",
            )
        if isinstance(pin_mode, GPIOPinMode):
            self._backend.set_gpio_pin_mode(self._identifier, pin_mode)

    @property
    def digital_state(self) -> bool:
        """Get the digital state of the pin."""
        self._require_pin_modes({
            GPIOPinMode.DIGITAL_OUTPUT,
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_INPUT_PULLDOWN},
        )

        # Behave differently depending on the hardware mode.
        if self.mode is GPIOPinMode.DIGITAL_OUTPUT:
            return self._backend.get_gpio_pin_digital_state(self._identifier)

        return self._backend.read_gpio_pin_digital_state(self._identifier)

    @digital_state.setter
    def digital_state(self, state: bool) -> None:
        """Set the digital state of the pin."""
        self._require_pin_modes({GPIOPinMode.DIGITAL_OUTPUT})
        self._backend.write_gpio_pin_digital_state(self._identifier, state)

    @property
    def analogue_value(self) -> float:
        """Get the scaled analogue reading of the pin."""
        self._require_pin_modes({GPIOPinMode.ANALOGUE_INPUT})
        return self._backend.read_gpio_pin_analogue_value(self._identifier)

    @analogue_value.setter
    def analogue_value(self, new_value: float) -> None:
        """Set the analogue value of the pin."""
        self._require_pin_modes({
            GPIOPinMode.ANALOGUE_OUTPUT,
            GPIOPinMode.PWM_OUTPUT,
        })
        if new_value < 0 or new_value > 1:
            raise ValueError("An analogue pin value must be between 0 and 1.")

        if self.mode is GPIOPinMode.ANALOGUE_OUTPUT:
            self._backend.write_gpio_pin_dac_value(
                self._identifier,
                new_value,
            )
        else:
            # We must be a PWM_OUTPUT
            self._backend.write_gpio_pin_pwm_value(
                self._identifier,
                new_value,
            )

    @property
    def firmware_modes(self) -> Set[FirmwareMode]:
        """Get the supported firmware modes."""
        return self._firmware_modes

    @firmware_modes.setter
    def firmware_modes(self, modes: Set[FirmwareMode]) -> None:
        """Set the supported firmware modes."""
        self._firmware_modes = modes
