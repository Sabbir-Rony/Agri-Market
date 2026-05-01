# Pre-Harvest Marketplace

A B2B/B2C pre-harvest agricultural marketplace with escrow-like split payments, role-based dashboards, order approval, delivery tracking, and crop-loss insurance claims.

## Features

### For Farmers
- List pre-harvest products with expected quantity, harvest date, and pricing
- Enable crop insurance on any product
- Review and approve / reject incoming buyer orders
- Track deliveries and receive split payments (30% advance + 70% on delivery)
- Submit crop-loss insurance claims

### For Buyers
- Browse and search pre-harvest products (by name, category, location, insurance)
- Place advance orders — pay 30% now, 70% on delivery
- Track order status through the full lifecycle
- View payment history and dashboard

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, SQLAlchemy (async), asyncpg / aiosqlite |
| Auth | JWT (access + refresh tokens) |
| Frontend | React 18, Vite, Zustand, TanStack Query, Tailwind CSS |
| Database | SQLite (local dev) → Postgres (Render / any Postgres host) |

---

## Local Development

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → API: http://localhost:8000
# → Docs: http://localhost:8000/docs

# 2. Frontend  (separate terminal)
cd frontend
npm install
npm run dev
# → UI: http://localhost:5173
```

The Vite dev server proxies `/api` and `/uploads` to port 8000, so everything works on `localhost:5173`.

---

## Deploy to Production

See **[DEPLOY.md](DEPLOY.md)** for step-by-step instructions.

- **Backend** → Render (free tier, includes Postgres)
- **Frontend** → Vercel (free tier)
- `render.yaml` in this folder is the Render Blueprint — one click creates the database + web service together.

---

## Order Flow

```
Buyer places order
       ↓
[advance_pending] → Buyer pays 30%
       ↓
[awaiting_farmers_approval] → Farmer approves
       ↓
[approved] → Farmer creates delivery
       ↓
[scheduled] → out_for_delivery → delivered
       ↓
[delivered_pending_final_payment] → Buyer pays 70%
       ↓
[completed]
```

---

## API Reference

Start the backend and open **http://localhost:8000/docs** for the full interactive Swagger UI.

Key endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register (farmer / buyer) |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/products` | List products (supports filters) |
| POST | `/api/products` | Create product (farmer) |
| POST | `/api/orders` | Place order (buyer) |
| POST | `/api/payments/advance` | Pay 30% advance (buyer) |
| PATCH | `/api/orders/{id}/approve` | Approve order (farmer) |
| POST | `/api/deliveries` | Schedule delivery (farmer) |
| PATCH | `/api/deliveries/{id}/status` | Update delivery status (farmer) |
| POST | `/api/payments/final` | Pay 70% final (buyer) |
| POST | `/api/claims` | Submit insurance claim (farmer) |
| GET | `/api/dashboard/buyer` | Buyer stats |
| GET | `/api/dashboard/farmer` | Farmer stats |
