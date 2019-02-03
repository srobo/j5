"""Test the Dummy Backend Group."""

from j5.backends.dummy import DummyEnvironment


def test_dummy_environment():
    """Test that the dummy environment exists."""
    env = DummyEnvironment

    assert len(env.supported_boards) > 0
