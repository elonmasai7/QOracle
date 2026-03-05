from backend.services.webhook_signing import build_webhook_signature


def test_signature_format_and_determinism():
    payload = '{"event":"risk.completed","id":"1"}'
    sig1 = build_webhook_signature("whsec_test", payload, 1700000000)
    sig2 = build_webhook_signature("whsec_test", payload, 1700000000)

    assert sig1 == sig2
    assert sig1.startswith("t=1700000000,v1=")
