"""Unit tests for the security layer (no network, no database).

Implements plan cases UT-SEC-01..04. Fast and self-contained, so they run on
every CI push.
"""
import pytest
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)


# UT-SEC-01 — password hashing round-trip
def test_password_hash_roundtrip():
    h = hash_password("Sup3r-Secret")
    assert h != "Sup3r-Secret"                 # never stored in plaintext
    assert verify_password("Sup3r-Secret", h)  # correct password verifies
    assert not verify_password("wrong", h)     # wrong password fails


# UT-SEC-02 — token type claims
def test_token_type_claims():
    access = decode_token(create_access_token("user-1"))
    refresh = decode_token(create_refresh_token("user-1"))
    assert access["type"] == "access"
    assert refresh["type"] == "refresh"
    assert access["sub"] == "user-1"


# UT-SEC-03 — decoding an invalid / tampered token returns None
def test_decode_invalid_token():
    assert decode_token("not-a-real-token") is None
    good = create_access_token("user-1")
    assert decode_token(good + "tampered") is None


# UT-SEC-04 — a refresh token must not be usable as an access token.
# get_current_user requires type == "access"; verify the discriminator here.
def test_refresh_token_is_not_an_access_token():
    refresh_payload = decode_token(create_refresh_token("user-1"))
    assert refresh_payload["type"] != "access"   # would be rejected with 401
