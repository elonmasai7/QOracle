import csv
import io
import json
import uuid
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt, jwt_required
from ..models import RiskResult, Portfolio
from ..services.compliance import build_compliance_report


report_bp = Blueprint("report", __name__, url_prefix="/api/v1/reports")


@report_bp.get("/compliance/<portfolio_id>")
@jwt_required()
def compliance_report(portfolio_id):
    claims = get_jwt()
    tenant_id = claims["tenant_id"]

    pf = Portfolio.query.filter_by(id=uuid.UUID(portfolio_id), tenant_id=uuid.UUID(tenant_id)).first()
    if not pf:
        return jsonify({"error": "portfolio_not_found"}), 404

    rr = (
        RiskResult.query.filter_by(portfolio_id=uuid.UUID(portfolio_id), tenant_id=uuid.UUID(tenant_id))
        .order_by(RiskResult.created_at.desc())
        .first()
    )
    if not rr:
        return jsonify({"error": "risk_result_not_found"}), 404

    payload = {
        "var_95": rr.var_95,
        "var_99": rr.var_99,
        "cvar_95": rr.cvar_95,
        "expected_shortfall": rr.expected_shortfall,
        "liquidity_risk": rr.liquidity_risk,
        "credit_risk": rr.credit_risk,
        "volatility_forecast": rr.volatility_forecast,
        "composite_risk_score": rr.composite_risk_score,
        "mode": rr.mode,
    }

    report = build_compliance_report("tenant", pf.name, payload)
    fmt = request.args.get("format", "json")

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["metric", "value"])
        for k, v in payload.items():
            writer.writerow([k, v])
        return Response(output.getvalue(), mimetype="text/csv")

    if fmt == "pdf":
        # Placeholder for real PDF generator like WeasyPrint.
        return Response(f"PDF generation queued for portfolio {pf.name}", mimetype="application/pdf")

    return Response(json.dumps(report, indent=2), mimetype="application/json")
