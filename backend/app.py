import logging
from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from .config import Config
from .extensions import db, jwt, limiter, metrics
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
from .routes.security_routes import security_bp


OPENAPI_DOC = {
    "openapi": "3.0.3",
    "info": {"title": "QuantumRisk Oracle API", "version": "1.1.0"},
    "paths": {
        "/api/v1/auth/login": {"post": {"summary": "Login and get JWT"}},
        "/api/v1/auth/me": {"get": {"summary": "Authenticated user profile"}},
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
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(security_bp)

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
            db.create_all()
        except SQLAlchemyError as exc:
            logging.getLogger(__name__).warning("Database initialization skipped: %s", exc)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
