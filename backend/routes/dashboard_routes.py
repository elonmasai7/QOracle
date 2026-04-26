from flask import Blueprint, jsonify, request
from ..services.platform_data import build_dashboard_snapshot


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")


@dashboard_bp.get("/overview")
def overview():
    tenant_id = request.args.get("tenant_id")
    return jsonify(build_dashboard_snapshot(tenant_id))
