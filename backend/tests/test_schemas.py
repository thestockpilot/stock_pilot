"""Unit tests for request-schema validation (no network, no database).

Implements plan cases UT-SCH-01..02.
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest


# UT-SCH-01 — self-registration cannot request the admin role
def test_register_rejects_admin_role():
    with pytest.raises(ValidationError):
        RegisterRequest(full_name="X", email="x@example.com",
                        password="password123", role="admin")


def test_register_allows_investor_and_analyst():
    for role in ("investor", "analyst"):
        req = RegisterRequest(full_name="X", email="x@example.com",
                              password="password123", role=role)
        assert req.role == role


def test_register_defaults_to_investor():
    req = RegisterRequest(full_name="X", email="x@example.com", password="password123")
    assert req.role == "investor"


# UT-SCH-02 — malformed email is rejected before any DB access
def test_login_rejects_bad_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="whatever")
