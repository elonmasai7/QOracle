from backend.services.security import (
    generate_api_key_token,
    hash_api_key_token,
    verify_api_key_token,
)


def test_api_key_hash_verify_roundtrip():
    token = generate_api_key_token()
    token_hash = hash_api_key_token(token)
    assert verify_api_key_token(token, token_hash)
    assert not verify_api_key_token(token + "x", token_hash)
