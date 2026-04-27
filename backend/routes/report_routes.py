import csv
import io
import json
import uuid
from flask import Blueprint, jsonify, request, Response
from ..auth import auth_required, get_auth_context
from ..extensions import db
from ..models import Report, RiskResult, Portfolio
from ..services.compliance import build_compliance_report
from ..services.platform_data import build_dashboard_snapshot


report_bp = Blueprint("report", __name__, url_prefix="/api/v1/reports")


@report_bp.get("/compliance/<portfolio_id>")
@auth_required
def compliance_report(portfolio_id):
    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]

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
    report_location = f"/api/v1/reports/compliance/{portfolio_id}?format={fmt}"

    report_row = Report(
        tenant_id=uuid.UUID(tenant_id),
        portfolio_id=uuid.UUID(portfolio_id),
        format=fmt,
        location=report_location,
        report_type="compliance",
    )
    db.session.add(report_row)
    db.session.commit()

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["metric", "value"])
        for k, v in payload.items():
            writer.writerow([k, v])
        return Response(output.getvalue(), mimetype="text/csv")

    if fmt == "pdf":
        from ..services.pdf_report import generate_compliance_pdf

        pdf_data = generate_compliance_pdf(report)
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=compliance_report_{portfolio_id}.pdf"
            },
        )

    return Response(json.dumps(report, indent=2), mimetype="application/json")


@report_bp.get("/library")
def report_library():
    try:
        ctx = get_auth_context()
        snapshot = build_dashboard_snapshot(ctx.get("tenant_id"))
        tenant_id = ctx.get("tenant_id")
        if tenant_id:
            report_rows = (
                Report.query.filter_by(tenant_id=uuid.UUID(str(tenant_id)))
                .order_by(Report.created_at.desc())
                .limit(10)
                .all()
            )
            if report_rows:
                return jsonify(
                    [
                        {
                            "title": f"{row.report_type.title()} report",
                            "updatedAt": row.created_at.isoformat(),
                            "format": row.format.upper(),
                            "owner": "System",
                            "location": row.location,
                        }
                        for row in report_rows
                    ]
                )
    except Exception:
        snapshot = build_dashboard_snapshot(None)
    return jsonify(snapshot["reports"])
