"""Orientation classes to represent rotations in space."""

from typing import Tuple

from pyquaternion import Quaternion

ThreeTuple = Tuple[float, float, float]
RotationMatrix = Tuple[ThreeTuple, ThreeTuple, ThreeTuple]


class Orientation:
    """
    Represents an orientation in 3D space.

    Uses a unit quaternion as an internal representation.
    """

    def __init__(self, orientation: Quaternion):
        self._quaternion = orientation

    @property
    def rotation_matrix(self) -> RotationMatrix:
        """
        Get the rotation matrix represented by this orientation.

        Returns:
            A 3x3 rotation matrix as a tuple of tuples.
        """
        r_m = self._quaternion.rotation_matrix
        return (
            (r_m[0][0], r_m[0][1], r_m[0][2]),
            (r_m[1][0], r_m[1][1], r_m[1][2]),
            (r_m[2][0], r_m[2][1], r_m[2][2]),
        )

    @property
    def yaw_pitch_roll(self) -> ThreeTuple:
        """
        Get the equivalent yaw-pitch-roll angles in radians.

        Specifically, intrinsic Tait-Bryan angles following the z-y'-x'' convention.

        See pyquaternion for details.
        """
        return self._quaternion.yaw_pitch_roll

    @property
    def yaw(self) -> float:
        """Rotation angle around the z-axis in radians."""
        return self.yaw_pitch_roll[0]

    @property
    def pitch(self) -> float:
        """Rotation angle around the y'-axis in radians."""
        return self.yaw_pitch_roll[1]

    @property
    def roll(self) -> float:
        """Rotation angle around the x''-axis in radians."""
        return self.yaw_pitch_roll[2]

    @property
    def rot_x(self) -> float:
        """Returns the rotation around the x axis in radians."""
        return self.pitch

    @property
    def rot_y(self) -> float:
        """Returns the rotation around the y axis in radians."""
        return self.yaw

    @property
    def rot_z(self) -> float:
        """Returns the rotation around the z axis in radians."""
        return self.roll

    @property
    def quaternion(self) -> Quaternion:
        """The quaternion representing the underlying rotation."""
        return self._quaternion

    def __repr__(self) -> str:
        """
        A string representation.

        Note that the actual parameters used to construct this are not
        used, because this is likely to confuse students.
        """
        return f"Orientation(" \
               f"rot_x={self.rot_x}, " \
               f"rot_y={self.rot_y}, " \
               f"rot_z={self.rot_z})"
