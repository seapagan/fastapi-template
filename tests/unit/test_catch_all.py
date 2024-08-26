"""Test the 'catch all' function."""

import pytest
from fastapi import HTTPException, status

from app.resources.config_error import catch_all


@pytest.mark.unit
def test_catch_all() -> None:
    """Test the catch_all function.

    We're just testing that it raises an HTTPException.
    """
    with pytest.raises(HTTPException) as exc:
        catch_all()

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.detail == (
        "ERROR: Cannot connect to the database! Have you set it up properly?"
    )
