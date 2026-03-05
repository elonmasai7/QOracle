import uuid
from flask import Blueprint, jsonify, request
from ..auth import auth_required, get_auth_context, role_required
from ..extensions import db
from ..models import WebhookSubscription
from ..services.audit import write_audit_log
from ..services.security import generate_webhook_secret


webhook_bp = Blueprint("webhook", __name__, url_prefix="/api/v1/webhooks")


@webhook_bp.post("/risk-events")
@auth_required
def risk_events():
    payload = request.get_json(force=True)
    return jsonify({"accepted": True, "event": payload.get("event", "unknown")}), 202


@webhook_bp.post("/subscriptions")
@auth_required
@role_required("admin")
def create_subscription():
    ctx = get_auth_context()
    tenant_id = uuid.UUID(ctx["tenant_id"])

    payload = request.get_json(force=True)
    target_url = payload.get("target_url", "")
    if not target_url.startswith("http"):
        return jsonify({"error": "invalid_target_url"}), 400

    signing_secret = generate_webhook_secret()
    row = WebhookSubscription(
        tenant_id=tenant_id,
        target_url=target_url,
        event_type=payload.get("event_type", "risk.completed"),
        signing_secret=signing_secret,
        active=True,
    )
    db.session.add(row)
    db.session.commit()

    write_audit_log(
        tenant_id,
        "webhook_subscription_create",
        "webhook",
        {"subscription_id": str(row.id), "target_url": row.target_url},
        user_id=ctx.get("user_id"),
    )

    return (
        jsonify(
            {
                "id": str(row.id),
                "target_url": row.target_url,
                "event_type": row.event_type,
                "signing_secret": signing_secret,
                "note": "Store this signing secret securely; shown once.",
            }
        ),
        201,
    )


@webhook_bp.get("/subscriptions")
@auth_required
@role_required("admin")
def list_subscriptions():
    ctx = get_auth_context()
    tenant_id = uuid.UUID(ctx["tenant_id"])

    rows = WebhookSubscription.query.filter_by(tenant_id=tenant_id).order_by(WebhookSubscription.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": str(r.id),
                "target_url": r.target_url,
                "event_type": r.event_type,
                "active": r.active,
                "last_status": r.last_status,
                "last_attempt_at": r.last_attempt_at.isoformat() if r.last_attempt_at else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )


@webhook_bp.post("/subscriptions/<subscription_id>/deactivate")
@auth_required
@role_required("admin")
def deactivate_subscription(subscription_id):
    ctx = get_auth_context()
    tenant_id = uuid.UUID(ctx["tenant_id"])

    row = WebhookSubscription.query.filter_by(
        id=uuid.UUID(subscription_id),
        tenant_id=tenant_id,
    ).first()
    if not row:
        return jsonify({"error": "subscription_not_found"}), 404

    row.active = False
    db.session.commit()
    write_audit_log(
        tenant_id,
        "webhook_subscription_deactivate",
        "webhook",
        {"subscription_id": subscription_id},
        user_id=ctx.get("user_id"),
    )
    return jsonify({"deactivated": True})
