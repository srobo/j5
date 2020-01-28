"""Tests for orientation class"""
from math import pi
from pyquaternion import Quaternion
from random import random, randint

from j5.vision.orientation import Orientation


def get_random_coord() -> float:
    """Get a random float between -8 and 8."""
    return (random() - 0.5) * randint(0, 2 * 8)


def get_random_angle() -> float:
    """Get a random float between 0 and 2π."""
    return random() * 2 * pi


def get_random_quaternion() -> Quaternion:
    """Generate a valid quaternion."""
    return Quaternion(axis=[get_random_coord()] * 3, angle=get_random_angle())


def test_quaternion() -> None:
    """Test the quaternion property of the Orientation class."""
    q = get_random_quaternion()
    assert q == Orientation(q).quaternion


def test_matrix() -> None:
    """Test the matrix property of the Orientation class"""
    q = get_random_quaternion()
    assert q.rotation_matrix == Orientation(q).matrix


def test_yaw_pitch_roll() -> None:
    """Test the yaw_pitch_roll property of the Orientation class"""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll == Orientation(q).yaw_pitch_roll


def test_yaw() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[0] == Orientation(q).yaw


def test_pitch() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[1] == Orientation(q).pitch


def test_roll() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[2] == Orientation(q).roll


def test_rot_x() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[1] == Orientation(q).rot_x


def test_rot_y() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[0] == Orientation(q).rot_y


def test_rot_z() -> None:
    """Test the yaw property of the Orientation class."""
    q = get_random_quaternion()
    assert q.yaw_pitch_roll[2] == Orientation(q).rot_z


def test_repr() -> None:
    """Test the yaw property of the Orientation class."""
    o = Orientation(get_random_quaternion())
    assert repr(o) == f"Orientation(" \
                      f"x_radians={o.rot_x}, " \
                      f"y_radians={o.rot_y}, " \
                      f"z_radians={o.rot_z}" \
                      f")"
