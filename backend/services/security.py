import secrets
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def generate_api_key_token(prefix: str = "qro_live") -> str:
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key_token(raw_key: str) -> str:
    return generate_password_hash(raw_key)


def verify_api_key_token(raw_key: str, token_hash: str) -> bool:
    return check_password_hash(token_hash, raw_key)


def generate_webhook_secret(prefix: str = "whsec") -> str:
    return f"{prefix}_{secrets.token_urlsafe(24)}"
