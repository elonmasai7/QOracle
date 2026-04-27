import logging
from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from .config import Config
from .extensions import db, jwt, limiter, metrics
from .models import Membership, Tenant, User
from .services.security import hash_password
from .services.logging_config import configure_logging
from .routes.auth_routes import auth_bp
from .routes.dashboard_routes import dashboard_bp
from .routes.portfolio_routes import portfolio_bp
from .routes.risk_routes import risk_bp
from .routes.report_routes import report_bp
from .routes.billing_routes import billing_bp
from .routes.webhook_routes import webhook_bp
from .routes.api_key_routes import api_key_bp
from .routes.explain_routes import explain_bp
from .routes.org_routes import org_bp
from .routes.security_routes import security_bp


OPENAPI_DOC = {
    "openapi": "3.0.3",
    "info": {"title": "QuantumRisk Oracle API", "version": "1.1.0"},
    "paths": {
        "/api/v1/auth/login": {"post": {"summary": "Login and get JWT"}},
        "/api/v1/auth/me": {"get": {"summary": "Authenticated user profile"}},
        "/api/v1/organizations/current": {"get": {"summary": "Current organization and memberships"}},
        "/api/v1/dashboard/overview": {"get": {"summary": "Dashboard overview snapshot"}},
        "/api/v1/api-keys": {"post": {"summary": "Create enterprise API key"}, "get": {"summary": "List API keys"}},
        "/api/v1/api-keys/{api_key_id}/revoke": {"post": {"summary": "Revoke API key"}},
        "/api/v1/portfolios/upload": {"post": {"summary": "Upload CSV portfolio"}},
        "/api/v1/portfolios/validate": {"post": {"summary": "Validate portfolio payload"}},
        "/api/v1/risk/run": {"post": {"summary": "Run risk job"}},
        "/api/v1/risk/scenarios": {"get": {"summary": "List standard stress scenarios"}},
        "/api/v1/reports/compliance/{portfolio_id}": {"get": {"summary": "Compliance report (JSON/CSV/PDF)"}},
        "/api/v1/reports/library": {"get": {"summary": "List report library"}},
        "/api/v1/security/overview": {"get": {"summary": "Security and compliance overview"}},
        "/api/v1/webhooks/subscriptions": {"post": {"summary": "Create outbound signed webhook"}, "get": {"summary": "List subscriptions"}},
        "/api/v1/explain/credit": {"post": {"summary": "Credit model SHAP/local explanation"}},
        "/api/v1/explain/credit/batch": {"post": {"summary": "Batch explainability and global drivers"}},
    },
}

DEMO_USERS = [
    {
        "tenant_name": "Helios Treasury",
        "plan": "enterprise",
        "email": "admin@helios-oracle.com",
        "password": "QuantumRisk!2026",
        "role": "admin",
    },
    {
        "tenant_name": "Helios Treasury",
        "plan": "enterprise",
        "email": "analyst@helios-oracle.com",
        "password": "QuantumRisk!2026",
        "role": "analyst",
    },
    {
        "tenant_name": "Northbridge Capital",
        "plan": "institutional",
        "email": "auditor@northbridge-capital.com",
        "password": "QuantumRisk!2026",
        "role": "auditor",
    },
]


def ensure_demo_users() -> None:
    if User.query.first():
        return

    for record in DEMO_USERS:
        tenant = Tenant.query.filter_by(name=record["tenant_name"]).first()
        if not tenant:
            tenant = Tenant(name=record["tenant_name"], plan=record["plan"])
            db.session.add(tenant)
            db.session.flush()

        user = User(
            tenant_id=tenant.id,
            email=record["email"],
            password_hash=hash_password(record["password"]),
            role=record["role"],
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(
            Membership(
                tenant_id=tenant.id,
                user_id=user.id,
                role=record["role"],
                status="active",
                is_default=True,
            )
        )

    db.session.commit()


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    configure_logging()

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    metrics.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_key_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(security_bp)

    @app.after_request
    def add_cors_headers(response):
        origin = app.config.get("FRONTEND_ORIGIN", "http://localhost:5173")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "quantumrisk-oracle-backend", "mode": app.config.get("QUANTUM_MODE", "hybrid")})

    @app.get("/health/ready")
    def readiness():
        return jsonify({"status": "ready"})

    @app.get("/openapi.json")
    def openapi():
        return jsonify(OPENAPI_DOC)

    with app.app_context():
        try:
            if app.config.get("ENV") in {"dev", "test"}:
                db.create_all()
                ensure_demo_users()
        except SQLAlchemyError as exc:
            logging.getLogger(__name__).warning("Database initialization skipped: %s", exc)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
