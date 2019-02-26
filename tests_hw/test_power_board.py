from time import sleep
from datetime import timedelta
from typing import cast
from j5.boards.sr.v4.power_board import PowerBoard
from j5.backends.hardware.sr.v4.power_board import SRV4PowerBoardHardwareBackend


def test_power_board():
    board = cast(PowerBoard, SRV4PowerBoardHardwareBackend.discover()[0])
    b = cast(SRV4PowerBoardHardwareBackend, board._backend)
    try:
        b.get_button_state(board, 1)
    except Exception as e:
        print(str(e))
    while True:
        print(f"Serial number: {board.serial}")
        print(f"Firmware version: {b.firmware_version}")
        for i in range(6):
            b.set_power_output_enabled(board, i, True)
            print(f"Output {i} on")
            sleep(0.5)
        for i in range(6):
            print(f"Output {i} current: {b.get_power_output_current(board, i)} A")
        for i in range(6):
            b.set_power_output_enabled(board, i, False)
            print(f"Output {i} off")
            sleep(0.5)
        print(f"Buzz")
        b.buzz(board, 0, timedelta(seconds=0.25), 1046)
        b.buzz(board, 0, timedelta(seconds=0.25), 1318)
        b.buzz(board, 0, timedelta(seconds=0.25), 1567)
        b.buzz(board, 0, timedelta(seconds=0.25), 2093)
        sleep(1.5)
        print(f"Start button pressed: {b.get_button_state(board, 0)}")
        print(f"Battery voltage: {b.get_battery_sensor_voltage(board, 0)} V")
        print(f"Battery current: {b.get_battery_sensor_current(board, 0)} A")
        for i in range(2):
            b.set_led_state(board, i, True)
            print(f"LED {i} on")
            sleep(0.5)
        for i in range(2):
            b.set_led_state(board, i, False)
            print(f"LED {i} off")
