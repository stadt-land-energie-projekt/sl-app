"""Conftest file holding fixtures used in different tests."""

import pytest

from slapp.users.models import User
from slapp.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir) -> None:  # noqa: ANN001, PT004
    """Return media root."""
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture()
def user(db) -> User:  # noqa: ARG001, ANN001
    """Return user factory."""
    return UserFactory()
