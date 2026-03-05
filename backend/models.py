import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from .extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Tenant(db.Model):
    __tablename__ = "tenants"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(50), nullable=False, default="starter")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tenants.id"), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="analyst")
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
    portfolio_id = db.Column(UUID(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    asset_class = db.Column(db.String(50), nullable=False, default="equity")


class RiskResult(BaseModel):
    __tablename__ = "riskresults"
    portfolio_id = db.Column(UUID(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    var_95 = db.Column(db.Float, nullable=False)
    var_99 = db.Column(db.Float, nullable=False)
    cvar_95 = db.Column(db.Float, nullable=False)
    expected_shortfall = db.Column(db.Float, nullable=False)
    liquidity_risk = db.Column(db.Float, nullable=False)
    credit_risk = db.Column(db.Float, nullable=False)
    volatility_forecast = db.Column(db.Float, nullable=False)
    composite_risk_score = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String(30), nullable=False, default="classical")


class StressResult(BaseModel):
    __tablename__ = "stressresults"
    portfolio_id = db.Column(UUID(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    scenario = db.Column(db.String(100), nullable=False)
    pnl_impact = db.Column(db.Float, nullable=False)
    details = db.Column(db.JSON, nullable=False)


class ModelMetric(BaseModel):
    __tablename__ = "modelmetrics"
    model_name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(30), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)


class AuditLog(BaseModel):
    __tablename__ = "auditlogs"
    user_id = db.Column(UUID(as_uuid=True), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource = db.Column(db.String(255), nullable=False)
    metadata_json = db.Column(db.JSON, nullable=False, default={})


class Report(BaseModel):
    __tablename__ = "reports"
    portfolio_id = db.Column(UUID(as_uuid=True), db.ForeignKey("portfolios.id"), nullable=False)
    format = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(512), nullable=False)
    report_type = db.Column(db.String(50), nullable=False, default="regulatory")


class BillingRecord(BaseModel):
    __tablename__ = "billingrecords"
    usage_type = db.Column(db.String(50), nullable=False)
    units = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
