import uuid
from ..extensions import db
from ..models import AuditLog


def write_audit_log(tenant_id, action, resource, metadata=None, user_id=None):
    entry = AuditLog(
        tenant_id=uuid.UUID(str(tenant_id)),
        user_id=uuid.UUID(str(user_id)) if user_id else None,
        action=action,
        resource=resource,
        metadata_json=metadata or {},
    )
    db.session.add(entry)
    db.session.commit()
