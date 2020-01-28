"""Tests for orientation class."""

from pyquaternion import Quaternion

from j5.vision.orientation import Orientation


def test_quaternion() -> None:
    """Test the quaternion property of the Orientation class."""
    q = Quaternion.random()
    assert q == Orientation(q).quaternion


def test_matrix() -> None:
    """Test the matrix property of the Orientation class."""
    q = Quaternion.random()
    assert q.rotation_matrix == Orientation(q).matrix


def test_yaw_pitch_roll() -> None:
    """Test the yaw_pitch_roll property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll == Orientation(q).yaw_pitch_roll


def test_yaw() -> None:
    """Test the yaw property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[0] == Orientation(q).yaw


def test_pitch() -> None:
    """Test the pitch property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[1] == Orientation(q).pitch


def test_roll() -> None:
    """Test the roll property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[2] == Orientation(q).roll


def test_rot_x() -> None:
    """Test the rot_x property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[1] == Orientation(q).rot_x


def test_rot_y() -> None:
    """Test the rot_y property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[0] == Orientation(q).rot_y


def test_rot_z() -> None:
    """Test the rot_z property of the Orientation class."""
    q = Quaternion.random()
    assert q.yaw_pitch_roll[2] == Orientation(q).rot_z


def test_repr() -> None:
    """Test the __repr__ method of the Orientation class."""
    o = Orientation(Quaternion.random())
    assert repr(o) == f"Orientation(" \
                      f"x_radians={o.rot_x}, " \
                      f"y_radians={o.rot_y}, " \
                      f"z_radians={o.rot_z}" \
                      f")"
