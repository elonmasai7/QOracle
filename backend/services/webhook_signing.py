import hashlib
import hmac


def build_webhook_signature(secret: str, payload_body: str, timestamp: int) -> str:
    signed_payload = f"{timestamp}.{payload_body}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"
