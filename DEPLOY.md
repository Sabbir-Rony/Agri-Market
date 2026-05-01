# Deploy Guide — Pre-Harvest Marketplace

Backend → **Render** (FastAPI + Postgres, Free)  
Frontend → **Vercel** (React, Free)  
Total time: ~20 minutes.

---

## Step 1 — Push to GitHub

```bash
cd pre_sale_and_buy
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

Replace `YOUR-USERNAME` and `YOUR-REPO` with your actual GitHub username and repo name.

---

## Step 2 — Deploy Backend on Render

### 2a. Create a Render account
Go to https://render.com and sign up (free).

### 2b. Deploy with Blueprint (one click)
1. Click **New +** → choose **Blueprint**
2. Connect your GitHub account, then select your repo
3. Render reads `render.yaml` and shows two resources:
   - `preharvest-db` (Postgres database, Free)
   - `preharvest-backend` (Web Service, Free)
4. Click **Apply** and wait 3–5 minutes for the first build

### 2c. Copy your backend URL
When the service shows **Live**, click `preharvest-backend` and copy its URL:
```
https://preharvest-backend.onrender.com
```

### Verify it works
Open this in your browser:
```
https://preharvest-backend.onrender.com/health
```
You should see: `{"status":"healthy"}`

> **Note:** Render free tier sleeps after 15 min of no traffic. First request after sleep takes ~30 seconds to wake up.

---

## Step 3 — Deploy Frontend on Vercel

### 3a. Create a Vercel account
Go to https://vercel.com and sign up with GitHub (free).

### 3b. Import your repo — choose ONE option

#### OPTION A — Deploy from repo root (easiest, recommended)
1. Click **Add New → Project**
2. Import your GitHub repo
3. Leave **Root Directory** as the default (do NOT change it)
4. Scroll to **Environment Variables** and add:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://preharvest-backend.onrender.com/api`  
     *(replace with YOUR Render URL from Step 2c, keep the `/api` at the end)*
5. Click **Deploy**

#### OPTION B — Deploy with frontend as root
1. Click **Add New → Project**, import your repo
2. Click **Edit** next to Root Directory → type `frontend` → Save
3. Framework: Vite (should auto-detect)
4. Add environment variable:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://preharvest-backend.onrender.com/api`
5. Click **Deploy**

### 3c. Your app is live
Vercel gives you a URL like `https://your-project.vercel.app`.  
Open it — you can now register, login, and use all features.

---

## Step 4 — Verify Everything Works

1. Open your Vercel URL
2. Click **Register** → fill in name, phone, password, select role → Register
3. Click **Login** → enter your credentials
4. If you're a **Farmer**: go to Dashboard → Add Product
5. If you're a **Buyer**: go to Browse Products → place an order

---

## Troubleshooting

### "/login" or "/register" shows "Not Found" after deploy
**Cause:** Vercel is not configured for SPA (single-page app) routing.  
**Fix:** Make sure you followed Option A or Option B exactly. Do NOT manually override the framework or build settings in Vercel UI — let `vercel.json` handle it.

### Red banner at top: "VITE_API_URL is not set"
Go to: Vercel → your project → **Settings → Environment Variables**  
→ Add `VITE_API_URL` = `https://your-backend.onrender.com/api`  
→ Go to **Deployments** → click the three dots on the latest deploy → **Redeploy**

### Red banner: "Backend unreachable" / Retry button
Render free tier sleeps after 15 minutes of no activity.  
Click the **Retry** button and wait 30 seconds. Or open `https://your-backend.onrender.com/health` directly to wake it up first.

### Login/register works but shows errors
Check that `VITE_API_URL` ends with `/api` (no trailing slash).  
Example: `https://preharvest-backend.onrender.com/api` ✓  
Not: `https://preharvest-backend.onrender.com/api/` ✗  
Not: `https://preharvest-backend.onrender.com` ✗

### "Database error" or registration fails
In Render Dashboard → `preharvest-backend` → Environment → check that `DATABASE_URL` is automatically set from the Postgres service. If missing, go to the Postgres service, copy the Internal Database URL, and paste it manually.

### Uploaded images disappear after Render restarts
Render free tier has ephemeral file storage — uploaded files are lost when the service restarts. For a production app, use Cloudinary or AWS S3 for image hosting.

---

## Local Development (no cloud needed)

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API runs at: http://localhost:8000
# Swagger docs: http://localhost:8000/docs

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# App runs at: http://localhost:5173
```

Local dev uses SQLite (no Postgres needed). The `.env` file in `backend/` is pre-configured.

---

## File Layout

```
pre_sale_and_buy/
├── vercel.json          ← Vercel SPA config for Option A (repo root deploy)
├── render.yaml          ← Render Blueprint: creates DB + backend in one click
├── README.md
├── DEPLOY.md            ← this file
├── backend/             ← FastAPI backend (deploys to Render)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/  ← /auth /products /orders /payments /claims /deliveries
│   │   ├── core/        ← config, database, security
│   │   ├── models/      ← SQLAlchemy ORM models
│   │   └── schemas/     ← Pydantic request/response schemas
│   ├── requirements.txt
│   └── .env             ← local dev only (SQLite + dev secret)
└── frontend/            ← React + Vite (deploys to Vercel)
    ├── vercel.json      ← Vercel SPA config for Option B (frontend root deploy)
    ├── vite.config.js
    ├── package.json
    └── src/
```
