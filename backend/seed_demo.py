import os

from backend.app import create_app
from backend.extensions import db
from backend.models import Membership, Tenant, User
from backend.services.security import hash_password


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


def seed_demo_users() -> None:
    app = create_app()

    with app.app_context():
        db.create_all()

        for record in DEMO_USERS:
            tenant = Tenant.query.filter_by(name=record["tenant_name"]).first()
            if not tenant:
                tenant = Tenant(name=record["tenant_name"], plan=record["plan"])
                db.session.add(tenant)
                db.session.flush()

            user = User.query.filter_by(email=record["email"]).first()
            if user:
                user.tenant_id = tenant.id
                user.role = record["role"]
                user.password_hash = hash_password(record["password"])
            else:
                user = User(
                    tenant_id=tenant.id,
                    email=record["email"],
                    password_hash=hash_password(record["password"]),
                    role=record["role"],
                )
                db.session.add(user)
                db.session.flush()

            membership = Membership.query.filter_by(user_id=user.id, tenant_id=tenant.id).first()
            if membership:
                membership.role = record["role"]
                membership.status = "active"
                membership.is_default = True
            else:
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

    print("Seeded demo users:")
    for record in DEMO_USERS:
        print(f"- {record['email']} / {record['password']} ({record['role']})")


if __name__ == "__main__":
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/quantumrisk-local.db")
    os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    seed_demo_users()
