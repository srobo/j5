"""Zoloto Marker Dictionary."""
from enum import IntEnum

from cv2 import aruco


class MarkerDict(IntEnum):
    DICT_APRILTAG_36H11 = aruco.DICT_APRILTAG_36H11