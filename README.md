# QuantumRisk Oracle

QuantumRisk Oracle is a U.S.-oriented enterprise SaaS platform for portfolio risk intelligence combining hybrid quantum-inspired Monte Carlo simulation, classical ML forecasting, real-time analytics, and compliance-ready reporting.

## Core Capabilities
- Multi-tenant portfolio ingestion (CSV now, API/ERP extensible)
- VaR (95%, 99%), CVaR, Expected Shortfall
- Liquidity risk and credit risk scoring
- LSTM volatility forecasting pipeline
- Bayesian macro stress scenarios for U.S. shocks
- Hybrid classical/quantum tail probability benchmark with fallback
- Compliance report exports (JSON/CSV/PDF placeholder)
- Async risk jobs via Celery + Redis
- Usage-based quantum billing records
- Enterprise API-key authentication (`X-API-Key`)
- Signed outbound webhook subscriptions (`risk.completed`)
- Real PDF compliance rendering
- SHAP explainability endpoints for credit risk model
- Prometheus metrics, structured JSON logs, audit trail records

## Architecture
- Frontend: React + TypeScript + Recharts
- Backend: Flask + JWT + RBAC + rate limiting
- Risk/ML: NumPy/SciPy + PyTorch + XGBoost + Qiskit
- Data: PostgreSQL (tenant-aware schema)
- Queue: Redis + Celery
- Infra: Docker, Docker Compose, Kubernetes, GitHub Actions CI/CD

## Project Structure
```text
quantumrisk-oracle/
├── backend/
├── worker/
├── frontend/
├── database/
├── k8s/
├── tests/
├── sample_data/
├── docs/
├── docker-compose.yml
├── .env
└── README.md
```

## Quick Start
1. Build and run:
```bash
docker compose up --build -d
```
2. Health check:
```bash
curl http://localhost:8000/health
```
3. Open API doc seed:
```bash
curl http://localhost:8000/openapi.json
```
4. Frontend:
- `http://localhost:3000`

## API Example Flow
1. Register tenant/user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"tenant_name":"Acme Treasury","email":"admin@acme.com","password":"S3cret!123","role":"admin"}'
```
2. Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@acme.com","password":"S3cret!123"}'
```
3. Upload portfolio CSV:
```bash
curl -X POST http://localhost:8000/api/v1/portfolios/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Core Portfolio" \
  -F "file=@sample_data/portfolio_sample.csv"
```
4. Run risk:
```bash
curl -X POST http://localhost:8000/api/v1/risk/run \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"portfolio_id":"<PORTFOLIO_UUID>","mode":"hybrid","paths":20000}'
```

## Compliance Mapping
- SEC: risk summary disclosure payload
- GAAP: structured report outputs and audit trace
- Basel III: VaR/CVaR/ES and stress support
- SOX: immutable event-style audit logging pattern

## Security Controls
- JWT authentication + role-based authorization
- Tenant scoping in queries
- API rate limiting and throttling hooks
- Input validation for upload format and payload types
- AES-256/TLS1.3 controls represented in configuration and report controls
- SOC 2-ready logical architecture (audit, isolation, traceability)

## Performance Targets Design Notes
- Classical risk path count 10k-100k with vectorized NumPy ops
- Hybrid mode includes quantum estimator benchmark + fallback
- Horizontal scalability via k8s HPA on backend/worker
- For 50k concurrent users: deploy managed Postgres/Redis, ingress autoscaling, CDN/WAF, and sharded task workers

## ML Pipeline
Training scripts:
- `backend/ml/training/train_volatility.py`
- `backend/ml/training/train_credit.py`
- `backend/ml/training/train_macro.py`

Registry artifacts:
- `volatility_vX.pt`
- `credit_vX.pkl`
- `macro_vX.pkl`
- metadata JSON files

## Tests
```bash
pytest -q
```

## Notes
- Quantum block uses Qiskit runtime-compatible design with safe classical fallback.
- PDF export endpoint generates binary PDF documents using ReportLab.
- ERP/API integrations should be implemented via dedicated ingestion connectors under `backend/routes` + `backend/services`.

## Enterprise Features
- API Key management: `/api/v1/api-keys` (create/list/revoke; admin role)
- Any protected endpoint supports JWT or API key auth
- Signed webhooks: configure `/api/v1/webhooks/subscriptions`; outgoing signature `t=<ts>,v1=<hmac>`
- Explainability:
1. `POST /api/v1/explain/credit`
2. `POST /api/v1/explain/credit/batch`
