"""Test the Dummy Backend Group."""

from j5.backends.dummy import DummyBackendGroup


def test_dummy_backend_group():
    """Test that the dummy backend group exists."""
    dbg = DummyBackendGroup

    assert len(dbg.supported_boards) > 0
