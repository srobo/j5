"""Test the base component classes."""


import pytest

from j5.components import (
    DerivedComponent,
    Interface,
    NotSupportedByComponentError,
)


class MyInterface(Interface):
    """An interface."""


class MyDerivedComponent(DerivedComponent):
    """A derived component."""

    @staticmethod
    def interface_class() -> type[Interface]:
        """Get the interface class that is required to use this component."""
        return MyInterface


def test_derived_component_identifier() -> None:
    """Test that derived components do not have an identifier."""
    mdc = MyDerivedComponent()

    with pytest.raises(NotSupportedByComponentError):
        mdc.identifier
