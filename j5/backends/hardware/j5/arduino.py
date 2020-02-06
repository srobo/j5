"""Base backend for Arduino Uno and its derivatives."""

from j5.components import LEDInterface

FIRST_ANALOGUE_PIN = 14

class ArduinoHardwareBackend(
    LEDInterface,
    GPIOInterface,
    SerialHardwareBackend,
):

