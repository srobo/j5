"""Test the base component classes."""

from j5.components.base import Component


def test_abstract_component():
    """Test that we can create an abstract component."""
    Component()
