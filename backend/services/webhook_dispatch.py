import json
import logging
import time
from datetime import datetime
from flask import current_app
import requests
from ..extensions import db
from ..models import WebhookSubscription
from .webhook_signing import build_webhook_signature


logger = logging.getLogger(__name__)
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
            timeout = current_app.config.get("WEBHOOK_REQUEST_TIMEOUT_SECONDS", 5)
            resp = requests.post(sub.target_url, data=body, headers=headers, timeout=timeout)
            sub.last_status = f"{resp.status_code}"
        except Exception as exc:
            sub.last_status = f"error:{type(exc).__name__}"
            logger.warning(
                "Webhook dispatch failed",
                extra={"target_url": sub.target_url, "event_type": event_type, "error": str(exc)},
            )
        sub.last_attempt_at = datetime.utcnow()

    db.session.commit()
