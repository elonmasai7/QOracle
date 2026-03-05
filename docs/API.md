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

## Billing
- `GET /billing/usage`

## Webhooks
- `POST /webhooks/risk-events`
