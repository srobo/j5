"""Test the base component classes."""

from typing import Type

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
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        return MyInterface


def test_derived_component_identifier() -> None:
    """Test that derived components do not have an identifier."""
    mdc = MyDerivedComponent()

    with pytest.raises(NotSupportedByComponentError):
        _ = mdc.identifier
