from datetime import datetime


def build_compliance_report(tenant_name, portfolio_name, risk_payload):
    return {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "frameworks": ["SEC", "GAAP", "Basel III", "SOX"],
        "tenant": tenant_name,
        "portfolio": portfolio_name,
        "risk_summary": risk_payload,
        "controls": {
            "encryption_at_rest": "AES-256",
            "encryption_in_transit": "TLS 1.3",
            "audit_retention": "7 years",
            "soc2_readiness": True,
            "tenant_isolation": True,
            "activity_traceability": True,
        },
    }
