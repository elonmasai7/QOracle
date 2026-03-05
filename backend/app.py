from flask import Flask, jsonify
from dotenv import load_dotenv
from .config import Config
from .extensions import db, jwt, limiter, metrics
from .services.logging_config import configure_logging
from .routes.auth_routes import auth_bp
from .routes.portfolio_routes import portfolio_bp
from .routes.risk_routes import risk_bp
from .routes.report_routes import report_bp
from .routes.billing_routes import billing_bp
from .routes.webhook_routes import webhook_bp


OPENAPI_DOC = {
    "openapi": "3.0.3",
    "info": {"title": "QuantumRisk Oracle API", "version": "1.0.0"},
    "paths": {
        "/api/v1/auth/login": {"post": {"summary": "Login and get JWT"}},
        "/api/v1/portfolios/upload": {"post": {"summary": "Upload CSV portfolio"}},
        "/api/v1/risk/run": {"post": {"summary": "Run risk job"}},
        "/api/v1/reports/compliance/{portfolio_id}": {"get": {"summary": "Compliance report"}},
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
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(webhook_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "quantumrisk-oracle-backend"})

    @app.get("/openapi.json")
    def openapi():
        return jsonify(OPENAPI_DOC)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
