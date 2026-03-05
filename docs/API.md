# API Overview

Base URL: `/api/v1`

## Auth
- `POST /auth/register`
- `POST /auth/login`

## Portfolios
- `POST /portfolios/upload` (multipart CSV)
- `GET /portfolios/`

## Risk
- `POST /risk/run`
- `GET /risk/task/{task_id}`

## Reports
- `GET /reports/compliance/{portfolio_id}?format=json|csv|pdf`

## Enterprise API Keys
- `POST /api-keys`
- `GET /api-keys`
- `POST /api-keys/{api_key_id}/revoke`

Protected endpoints accept either:
- `Authorization: Bearer <jwt>`
- `X-API-Key: qro_live_...`

## Outbound Webhooks (Signed)
- `POST /webhooks/subscriptions`
- `GET /webhooks/subscriptions`
- `POST /webhooks/subscriptions/{subscription_id}/deactivate`

Signature headers on outbound events:
- `X-QRO-Event`
- `X-QRO-Signature` with format `t=<unix_ts>,v1=<hmac_sha256>`

## Explainability (SHAP)
- `POST /explain/credit`
- `POST /explain/credit/batch`

## Billing
- `GET /billing/usage`

## Webhooks
- `POST /webhooks/risk-events`
