import uuid
from collections import defaultdict
from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from ..models import ApiKey, Asset, AuditLog, Portfolio, RiskResult, ScenarioTemplate, StressResult


def _default_snapshot() -> dict[str, Any]:
    return {
        "metrics": [
            {
                "id": "risk-score",
                "label": "Composite Risk Score",
                "value": "68.4",
                "delta": "+2.1%",
                "trend": "up",
                "metadata": "vs. prior close",
                "sparkline": [55, 57, 56, 58, 60, 62, 65, 68],
            },
            {
                "id": "var",
                "label": "Value at Risk",
                "value": "$12.8M",
                "delta": "-3.4%",
                "trend": "down",
                "metadata": "99% one-day VaR",
                "sparkline": [13.8, 13.4, 13.2, 12.9, 12.8, 12.8, 12.7, 12.8],
            },
            {
                "id": "shortfall",
                "label": "Expected Shortfall",
                "value": "$18.6M",
                "delta": "+1.2%",
                "trend": "up",
                "metadata": "tail conditional loss",
                "sparkline": [17.2, 17.4, 17.6, 17.9, 18.2, 18.1, 18.4, 18.6],
            },
            {
                "id": "vol",
                "label": "Forecast Volatility",
                "value": "22.4%",
                "delta": "+74 bps",
                "trend": "up",
                "metadata": "10-day forward",
                "sparkline": [19.1, 19.4, 20.2, 20.8, 21.4, 21.9, 22.1, 22.4],
            },
            {
                "id": "liquidity",
                "label": "Liquidity Stress",
                "value": "0.41",
                "delta": "stable",
                "trend": "neutral",
                "metadata": "bid-ask stress index",
                "sparkline": [0.34, 0.35, 0.36, 0.38, 0.39, 0.41, 0.41, 0.41],
            },
        ],
        "riskTrend": [
            {"label": "Jan", "risk": 54, "var95": 8.8},
            {"label": "Feb", "risk": 57, "var95": 9.1},
            {"label": "Mar", "risk": 60, "var95": 9.9},
            {"label": "Apr", "risk": 58, "var95": 9.4},
            {"label": "May", "risk": 63, "var95": 10.2},
            {"label": "Jun", "risk": 66, "var95": 10.8},
            {"label": "Jul", "risk": 68, "var95": 11.4},
            {"label": "Aug", "risk": 71, "var95": 11.8},
        ],
        "histogram": [
            {"bucket": "-6%", "frequency": 8},
            {"bucket": "-5%", "frequency": 16},
            {"bucket": "-4%", "frequency": 34},
            {"bucket": "-3%", "frequency": 62},
            {"bucket": "-2%", "frequency": 88},
            {"bucket": "-1%", "frequency": 102},
            {"bucket": "0%", "frequency": 76},
            {"bucket": "1%", "frequency": 43},
            {"bucket": "2%", "frequency": 21},
        ],
        "tailRisk": [
            {"percentile": "90", "loss": 5.2},
            {"percentile": "95", "loss": 8.1, "marker": "VaR"},
            {"percentile": "97.5", "loss": 10.7},
            {"percentile": "99", "loss": 12.8},
            {"percentile": "99.5", "loss": 18.6, "marker": "CVaR"},
        ],
        "heatmap": [
            {"x": "Rates", "y": "Rates", "value": 1},
            {"x": "Rates", "y": "FX", "value": 0.62},
            {"x": "Rates", "y": "Credit", "value": 0.58},
            {"x": "Rates", "y": "Equity", "value": 0.44},
            {"x": "FX", "y": "Rates", "value": 0.62},
            {"x": "FX", "y": "FX", "value": 1},
            {"x": "FX", "y": "Credit", "value": 0.37},
            {"x": "FX", "y": "Equity", "value": 0.51},
            {"x": "Credit", "y": "Rates", "value": 0.58},
            {"x": "Credit", "y": "FX", "value": 0.37},
            {"x": "Credit", "y": "Credit", "value": 1},
            {"x": "Credit", "y": "Equity", "value": 0.69},
            {"x": "Equity", "y": "Rates", "value": 0.44},
            {"x": "Equity", "y": "FX", "value": 0.51},
            {"x": "Equity", "y": "Credit", "value": 0.69},
            {"x": "Equity", "y": "Equity", "value": 1},
        ],
        "treemap": [
            {"name": "US Rates", "size": 34, "fill": "#2563EB"},
            {"name": "IG Credit", "size": 24, "fill": "#1D4ED8"},
            {"name": "Global Equity", "size": 18, "fill": "#0F766E"},
            {"name": "FX Overlay", "size": 12, "fill": "#0891B2"},
            {"name": "Cash Buffer", "size": 7, "fill": "#16A34A"},
            {"name": "Private Debt", "size": 5, "fill": "#D97706"},
        ],
        "scenarios": [
            {"name": "Fed +200bps", "base": -4.1, "stressed": -8.8},
            {"name": "Market Crash", "base": -7.4, "stressed": -18.6},
            {"name": "Liquidity Crunch", "base": -2.3, "stressed": -9.1},
            {"name": "Inflation Spike", "base": -3.8, "stressed": -7.2},
        ],
        "recommendations": [
            {
                "title": "Reduce sector concentration",
                "confidence": 92,
                "impact": 18,
                "rationale": "Equity beta contribution exceeds policy corridor under the market crash path by 320bps.",
                "action": "Apply Strategy",
            },
            {
                "title": "Increase cash buffer",
                "confidence": 88,
                "impact": 11,
                "rationale": "Liquidity stress remains elevated through the first three liquidation buckets.",
                "action": "Save Recommendation",
            },
            {
                "title": "Hedge FX exposure",
                "confidence": 85,
                "impact": 9,
                "rationale": "Cross-currency basis widening amplifies VaR in EMEA holdings under inflation shock scenarios.",
                "action": "Apply Strategy",
            },
            {
                "title": "Rebalance debt profile",
                "confidence": 81,
                "impact": 7,
                "rationale": "Credit spread widening path shows outsized drawdown concentration in lower-rated tranches.",
                "action": "Save Recommendation",
            },
        ],
        "stressCards": [
            {"name": "Fed hike +200bps", "shock": "Rates shock", "impact": "-8.8%", "severity": "medium"},
            {"name": "Market crash -20%", "shock": "Equity shock", "impact": "-18.6%", "severity": "high"},
            {"name": "Liquidity crunch", "shock": "Funding shock", "impact": "-9.1%", "severity": "high"},
            {"name": "Inflation spike", "shock": "Macro shock", "impact": "-7.2%", "severity": "medium"},
            {"name": "Credit spread widening", "shock": "Spread shock", "impact": "-6.4%", "severity": "medium"},
        ],
        "workflowSteps": [
            {"title": "Upload Portfolio", "status": "complete", "detail": "CSV holdings and benchmark mappings loaded."},
            {"title": "Validate Data", "status": "complete", "detail": "Holdings schema and price coverage validated."},
            {"title": "Configure Model", "status": "active", "detail": "25,000 paths, 99% interval, hybrid quantum enabled."},
            {"title": "Run Analysis", "status": "pending", "detail": "Awaiting final approval and scenario selection."},
        ],
        "reports": [
            {"title": "Board Risk Packet", "updatedAt": "2026-04-25 17:40 UTC", "format": "PDF", "owner": "Treasury Ops"},
            {"title": "Weekly VaR Distribution", "updatedAt": "2026-04-25 14:10 UTC", "format": "CSV", "owner": "Quant Research"},
            {"title": "Compliance Stress Review", "updatedAt": "2026-04-24 11:30 UTC", "format": "PDF", "owner": "Risk Control"},
        ],
        "auditLog": [
            {"event": "API key rotated", "actor": "A. Mensah", "timestamp": "09:12", "channel": "Security"},
            {"event": "Stress test executed", "actor": "M. Alvarez", "timestamp": "08:58", "channel": "Risk Engine"},
            {"event": "Portfolio import validated", "actor": "T. Shah", "timestamp": "08:41", "channel": "Portfolios"},
        ],
        "apiKeys": [
            {"name": "Treasury Workflow", "scope": "read:reports write:risk", "lastUsed": "11 minutes ago", "status": "Active"},
            {"name": "Audit Export", "scope": "read:audit", "lastUsed": "2 hours ago", "status": "Restricted"},
        ],
        "exposures": [
            {"desk": "Global Macro", "allocation": 31, "varContribution": 28},
            {"desk": "Credit Opportunities", "allocation": 24, "varContribution": 29},
            {"desk": "Rates Overlay", "allocation": 18, "varContribution": 16},
            {"desk": "EM FX", "allocation": 14, "varContribution": 18},
            {"desk": "Liquidity Reserve", "allocation": 13, "varContribution": 9},
        ],
    }


def build_dashboard_snapshot(tenant_id: str | None = None) -> dict[str, Any]:
    snapshot = _default_snapshot()
    if not tenant_id:
        return snapshot

    try:
        tenant_uuid = uuid.UUID(str(tenant_id))
        latest_result = (
            RiskResult.query.filter_by(tenant_id=tenant_uuid).order_by(RiskResult.created_at.desc()).first()
        )
        latest_stress = (
            StressResult.query.filter_by(tenant_id=tenant_uuid).order_by(StressResult.created_at.desc()).all()
        )
        audit_rows = (
            AuditLog.query.filter_by(tenant_id=tenant_uuid).order_by(AuditLog.created_at.desc()).limit(5).all()
        )
        api_keys = ApiKey.query.filter_by(tenant_id=tenant_uuid).order_by(ApiKey.created_at.desc()).limit(5).all()
        portfolios = Portfolio.query.filter_by(tenant_id=tenant_uuid).all()
        assets = Asset.query.filter_by(tenant_id=tenant_uuid).all()

        if latest_result:
            snapshot["metrics"] = [
                {
                    "id": "risk-score",
                    "label": "Composite Risk Score",
                    "value": f"{latest_result.composite_risk_score:.1f}",
                    "delta": "+1.9%",
                    "trend": "up",
                    "metadata": "current model composite",
                    "sparkline": [56, 58, 59, 61, 63, 65, 66, round(latest_result.composite_risk_score, 1)],
                },
                {
                    "id": "var",
                    "label": "Value at Risk",
                    "value": f"${latest_result.var_99:,.2f}",
                    "delta": "-2.4%",
                    "trend": "down",
                    "metadata": f"{int(latest_result.confidence_interval * 100)}% one-day VaR",
                    "sparkline": [latest_result.var_95 * 0.8, latest_result.var_95 * 0.86, latest_result.var_95 * 0.92, latest_result.var_99],
                },
                {
                    "id": "shortfall",
                    "label": "Expected Shortfall",
                    "value": f"${latest_result.expected_shortfall:,.2f}",
                    "delta": "+0.8%",
                    "trend": "up",
                    "metadata": "tail conditional loss",
                    "sparkline": [latest_result.cvar_95 * 0.7, latest_result.cvar_95 * 0.78, latest_result.cvar_95 * 0.84, latest_result.expected_shortfall],
                },
                {
                    "id": "vol",
                    "label": "Forecast Volatility",
                    "value": f"{latest_result.volatility_forecast * 100:.1f}%",
                    "delta": "+46 bps",
                    "trend": "up",
                    "metadata": "10-day forward",
                    "sparkline": [0.14, 0.16, 0.19, latest_result.volatility_forecast],
                },
                {
                    "id": "liquidity",
                    "label": "Liquidity Stress",
                    "value": f"{latest_result.liquidity_risk:.2f}",
                    "delta": "stable",
                    "trend": "neutral",
                    "metadata": "bid-ask stress index",
                    "sparkline": [0.25, 0.28, 0.33, latest_result.liquidity_risk],
                },
            ]
            snapshot["recommendations"] = latest_result.recommendations or snapshot["recommendations"]

        if latest_stress:
            snapshot["scenarios"] = [
                {
                    "name": row.scenario.replace("_", " ").title(),
                    "base": round(row.pnl_impact * 0.55, 2),
                    "stressed": round(row.pnl_impact, 2),
                }
                for row in latest_stress[:4]
            ]

        if audit_rows:
            snapshot["auditLog"] = [
                {
                    "event": row.action.replace("_", " ").title(),
                    "actor": str(row.user_id)[:8] if row.user_id else "System",
                    "timestamp": row.created_at.strftime("%H:%M"),
                    "channel": row.resource.title(),
                }
                for row in audit_rows
            ]

        if api_keys:
            snapshot["apiKeys"] = [
                {
                    "name": row.name,
                    "scope": row.role,
                    "lastUsed": row.last_used_at.strftime("%Y-%m-%d %H:%M") if row.last_used_at else "Never",
                    "status": "Active" if row.active else "Revoked",
                }
                for row in api_keys
            ]

        if portfolios:
            exposure = defaultdict(lambda: {"allocation": 0.0, "varContribution": 0.0})
            total_value = sum(asset.quantity * asset.price for asset in assets) or 1.0
            for asset in assets:
                bucket = asset.asset_class.title()
                weight = (asset.quantity * asset.price) / total_value
                exposure[bucket]["allocation"] += weight * 100
                exposure[bucket]["varContribution"] += weight * 110
            snapshot["exposures"] = [
                {
                    "desk": key,
                    "allocation": round(values["allocation"]),
                    "varContribution": round(min(values["varContribution"], 100)),
                }
                for key, values in exposure.items()
            ][:5] or snapshot["exposures"]

    except (ValueError, SQLAlchemyError):
        return snapshot

    return snapshot


def build_security_overview(tenant_id: str | None = None) -> dict[str, Any]:
    snapshot = build_dashboard_snapshot(tenant_id)
    return {
        "rbac": [
            {"role": "admin", "capabilities": ["manage_users", "rotate_keys", "approve_reports"]},
            {"role": "analyst", "capabilities": ["run_risk", "create_reports", "view_audit"]},
            {"role": "auditor", "capabilities": ["view_audit", "view_reports"]},
        ],
        "auditLog": snapshot["auditLog"],
        "apiKeys": snapshot["apiKeys"],
        "controls": [
            "JWT and API-key authentication",
            "Signed outbound webhooks",
            "Rate limiting and audit trails",
            "Compliance export governance",
        ],
    }


def stress_scenario_catalog() -> list[dict[str, Any]]:
    catalog = [
        {"name": "Fed hike +200bps", "type": "rates", "severity": "medium", "parameters": {"rates_bps": 200}},
        {"name": "Market crash -20%", "type": "equity", "severity": "high", "parameters": {"equity_drawdown_pct": -20}},
        {"name": "Liquidity crunch", "type": "liquidity", "severity": "high", "parameters": {"liquidity_haircut_pct": 40}},
        {"name": "Inflation spike", "type": "macro", "severity": "medium", "parameters": {"inflation_bps": 300}},
        {"name": "Credit spread widening", "type": "credit", "severity": "medium", "parameters": {"spread_bps": 180}},
    ]

    try:
        rows = ScenarioTemplate.query.order_by(ScenarioTemplate.created_at.desc()).all()
        if rows:
            return [
                {
                    "name": row.name,
                    "type": row.category,
                    "severity": row.severity,
                    "parameters": row.parameters,
                }
                for row in rows
            ]
    except SQLAlchemyError:
        return catalog

    return catalog


def validate_portfolio_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    required = {"symbol", "quantity", "price"}
    for index, row in enumerate(rows, start=1):
        missing = required - set(row)
        if missing:
            errors.append(f"row {index}: missing fields {sorted(missing)}")
            continue
        try:
            quantity = float(row["quantity"])
            price = float(row["price"])
            if quantity == 0:
                warnings.append(f"row {index}: zero quantity position")
            if price <= 0:
                errors.append(f"row {index}: price must be positive")
        except (TypeError, ValueError):
            errors.append(f"row {index}: quantity and price must be numeric")

    return {
        "valid": not errors,
        "rows": len(rows),
        "errors": errors,
        "warnings": warnings,
    }
