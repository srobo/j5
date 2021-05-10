"""Type stubs for PyQuaternion."""

from typing import List, Tuple

class Quaternion:

    # Note __init__ has many possible constructors. This is the one we use.
    def __init__(self, *, axis: Tuple[float, float, float], angle: float): ...

    @classmethod
    def random(cls) -> 'Quaternion': ...

    def rotate(self, q: 'Quaternion') -> 'Quaternion': ...

    @property
    def rotation_matrix(self) -> List[List[float]]: ...

    @property
    def yaw_pitch_roll(self) -> Tuple[float, float, float]: ...
