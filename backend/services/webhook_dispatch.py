import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
import requests
from ..extensions import db
from ..models import WebhookSubscription


logger = logging.getLogger(__name__)


def build_webhook_signature(secret: str, payload_body: str, timestamp: int) -> str:
    signed_payload = f"{timestamp}.{payload_body}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def dispatch_event(tenant_id, event_type: str, payload: dict):
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    timestamp = int(time.time())

    subscriptions = WebhookSubscription.query.filter_by(
        tenant_id=tenant_id,
        active=True,
        event_type=event_type,
    ).all()

    for sub in subscriptions:
        signature = build_webhook_signature(sub.signing_secret, body, timestamp)
        headers = {
            "Content-Type": "application/json",
            "X-QRO-Event": event_type,
            "X-QRO-Signature": signature,
        }
        try:
            resp = requests.post(sub.target_url, data=body, headers=headers, timeout=5)
            sub.last_status = f"{resp.status_code}"
        except Exception as exc:
            sub.last_status = f"error:{type(exc).__name__}"
            logger.warning(
                "Webhook dispatch failed",
                extra={"target_url": sub.target_url, "event_type": event_type, "error": str(exc)},
            )
        sub.last_attempt_at = datetime.utcnow()

    db.session.commit()
