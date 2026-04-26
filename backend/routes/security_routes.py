from flask import Blueprint, jsonify
from ..auth import auth_required, get_auth_context
from ..services.platform_data import build_security_overview


security_bp = Blueprint("security", __name__, url_prefix="/api/v1/security")


@security_bp.get("/overview")
@auth_required
def overview():
    ctx = get_auth_context()
    return jsonify(build_security_overview(ctx.get("tenant_id")))
