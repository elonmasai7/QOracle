from datetime import datetime
from functools import wraps
import uuid
from flask import jsonify, g, request
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request,
)
from .extensions import db
from .models import ApiKey
from .services.security import verify_api_key_token


def _resolve_auth_context():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            claims = get_jwt()
            return {
                "auth_type": "jwt",
                "user_id": identity,
                "tenant_id": claims.get("tenant_id"),
                "role": claims.get("role", ""),
            }
    except Exception:
        pass

    raw_key = request.headers.get("X-API-Key", "").strip()
    if raw_key:
        key_prefix = raw_key[:24]
        candidates = ApiKey.query.filter_by(key_prefix=key_prefix, active=True).all()
        now = datetime.utcnow()
        for candidate in candidates:
            if candidate.expires_at and candidate.expires_at < now:
                continue
            if verify_api_key_token(raw_key, candidate.key_hash):
                candidate.last_used_at = now
                db.session.commit()
                return {
                    "auth_type": "api_key",
                    "user_id": None,
                    "tenant_id": str(candidate.tenant_id),
                    "role": candidate.role,
                    "api_key_id": str(candidate.id),
                }

    return None


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ctx = _resolve_auth_context()
        if not ctx:
            return jsonify({"error": "authentication_required"}), 401
        g.auth_ctx = ctx
        return fn(*args, **kwargs)

    return wrapper


def get_auth_context():
    ctx = getattr(g, "auth_ctx", None)
    if ctx:
        return ctx
    # Safety fallback for direct calls without decorator.
    resolved = _resolve_auth_context()
    if not resolved:
        raise PermissionError("authentication_required")
    g.auth_ctx = resolved
    return resolved


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ctx = get_auth_context()
            role = ctx.get("role", "")
            if role not in allowed_roles:
                return jsonify({"error": "insufficient_role"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
