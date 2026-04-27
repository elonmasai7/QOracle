import uuid
from datetime import datetime
from sqlalchemy import Uuid
from .extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(Uuid(as_uuid=True), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Tenant(db.Model):
    __tablename__ = "tenants"
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(50), nullable=False, default="starter")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("tenants.id"), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="analyst")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Membership(db.Model):
    __tablename__ = "memberships"
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default="analyst")
    status = db.Column(db.String(30), nullable=False, default="active")
    is_default = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Portfolio(BaseModel):
    __tablename__ = "portfolios"
    name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(50), nullable=False, default="csv")


class Asset(BaseModel):
    __tablename__ = "assets"
    portfolio_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    asset_class = db.Column(db.String(50), nullable=False, default="equity")


class RiskResult(BaseModel):
    __tablename__ = "riskresults"
    portfolio_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    var_95 = db.Column(db.Float, nullable=False)
    var_99 = db.Column(db.Float, nullable=False)
    cvar_95 = db.Column(db.Float, nullable=False)
    expected_shortfall = db.Column(db.Float, nullable=False)
    liquidity_risk = db.Column(db.Float, nullable=False)
    credit_risk = db.Column(db.Float, nullable=False)
    volatility_forecast = db.Column(db.Float, nullable=False)
    composite_risk_score = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(30), nullable=False, default="classical")
    confidence_interval = db.Column(db.Float, nullable=False, default=0.99)
    simulation_paths = db.Column(db.Integer, nullable=False, default=10000)
    recommendations = db.Column(db.JSON, nullable=False, default=list)


class AnalysisRun(BaseModel):
    __tablename__ = "analysisruns"
    portfolio_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    task_id = db.Column(db.String(128), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="queued")
    engine = db.Column(db.String(30), nullable=False, default="hybrid")
    configuration = db.Column(db.JSON, nullable=False, default=dict)
    runtime_ms = db.Column(db.Integer, nullable=True)
    summary = db.Column(db.JSON, nullable=False, default=dict)


class StressResult(BaseModel):
    __tablename__ = "stressresults"
    portfolio_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    scenario = db.Column(db.String(100), nullable=False)
    pnl_impact = db.Column(db.Float, nullable=False)
    details = db.Column(db.JSON, nullable=False)


class ScenarioTemplate(BaseModel):
    __tablename__ = "scenariotemplates"
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="market")
    severity = db.Column(db.String(20), nullable=False, default="medium")
    parameters = db.Column(db.JSON, nullable=False, default=dict)


class ModelMetric(BaseModel):
    __tablename__ = "modelmetrics"
    model_name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(30), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)


class AuditLog(BaseModel):
    __tablename__ = "auditlogs"
    user_id = db.Column(Uuid(as_uuid=True), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource = db.Column(db.String(255), nullable=False)
    metadata_json = db.Column(db.JSON, nullable=False, default={})


class Report(BaseModel):
    __tablename__ = "reports"
    portfolio_id = db.Column(Uuid(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    format = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(512), nullable=False)
    report_type = db.Column(db.String(50), nullable=False, default="regulatory")


class BillingRecord(BaseModel):
    __tablename__ = "billingrecords"
    usage_type = db.Column(db.String(50), nullable=False)
    units = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


class ApiKey(BaseModel):
    __tablename__ = "apikeys"
    name = db.Column(db.String(100), nullable=False)
    key_prefix = db.Column(db.String(24), nullable=False, index=True)
    key_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="analyst")
    active = db.Column(db.Boolean, nullable=False, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)


class WebhookSubscription(BaseModel):
    __tablename__ = "webhooksubscriptions"
    target_url = db.Column(db.String(1024), nullable=False)
    event_type = db.Column(db.String(100), nullable=False, default="risk.completed")
    signing_secret = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    last_status = db.Column(db.String(50), nullable=True)
    last_attempt_at = db.Column(db.DateTime, nullable=True)
