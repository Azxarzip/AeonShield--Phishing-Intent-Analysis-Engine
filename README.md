# AeonShield: BEC & Phishing Detection Engine

**Repository:** [https://github.com/sayuj5/AeonShield--Phishing-Intent-Analysis-Engine](https://github.com/sayuj5/AeonShield--Phishing-Intent-Analysis-Engine)

![AeonShield Logo](AeonShiled%20Logo.png)

## Overview

AeonShield is a **machine learning pipeline** for detecting Business Email Compromise (BEC) and phishing. It combines technical features, **stylometry** (linguistic fingerprinting), **SHAP-based explainability**, and optional **organizational graph** checks. A **Streamlit** dashboard (`dashboard.py`) provides analysis, batch CSV processing, and model analytics.

The core classifier is a **Random Forest** tuned with class weights to emphasize **high recall** on malicious email, supported by synthetic and enhanced simulated datasets.

### Dashboard preview

![Dashboard Working](Dashboard%20Working.png)

---

## Requirements

- **Python 3.10+** (3.12 tested)
- pip

---

## Quick start (local)

### 1. Clone the repository

```bash
git clone https://github.com/sayuj5/AeonShield--Phishing-Intent-Analysis-Engine.git
cd AeonShield--Phishing-Intent-Analysis-Engine
```

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Train models and artifacts (full setup)

If you do not already have `model_stylometry.pkl`, `feature_names_stylometry.pkl`, and related files:

```bash
python data_simulator_enhanced.py   # Enhanced BEC-style dataset
python train_model_stylometry.py    # Phase 1 & 2 models + stylometry features
python train_phase3.py              # Organizational graph (Phase 3)
```

Pretrained artifacts may already be present in the repo; if `streamlit run` loads models successfully, you can skip retraining.

### 5. Run the dashboard

```bash
streamlit run dashboard.py
```

Open **http://localhost:8501** in your browser.

### Optional: Google Stitch (UI design)

The dashboard sidebar includes a **Stitch design lab** section. To use Google Stitch with tools or MCP, set an API key in your environment (never commit keys):

```powershell
# Windows PowerShell
$env:STITCH_API_KEY = "your-key-here"
```

```bash
# macOS / Linux
export STITCH_API_KEY="your-key-here"
```

See `stitch_integration.py` for MCP URL and notes. The official Node client is `@google/stitch-sdk`.

---

## Three-phase architecture

1. **Phase 1 — XAI:** SHAP explanations, risk level, forensic-style reason codes.  
2. **Phase 2 — Stylometry & ATO:** Baseline sender profiles and style drift; account-takeover-style signals combined with the classifier.  
3. **Phase 3 — Org graph:** Communication graph anomalies (requires `org_graph.pkl` from `train_phase3.py`).

---

## Dashboard modules

| Area | Description |
|------|-------------|
| **Dashboard** | Corpus metrics, charts (when `simulated_emails_enhanced.csv` is present), recent log preview. |
| **Analyze** | Single-email multi-phase scan with presets. |
| **Batch** | CSV upload; Kaggle-style columns (`body`, `label`, etc.) auto-detected when possible. |
| **Analytics** | Feature importance plots (`feature_importance_stylometry.csv` or `feature_importance.csv`). |
| **Profiles** | Baseline stylometry profiles from `profile_builder.pkl`. |
| **About** | Team and institution credits. |

---

## Key files

| File | Role |
|------|------|
| `dashboard.py` | Streamlit application |
| `feature_engineer.py` | Feature prep for training and inference |
| `stylometry_analyzer.py` | Linguistic features and profiles |
| `xai_explainer.py` | SHAP explainer wrapper |
| `ato_detector.py` | ATO / style-drift integration |
| `org_graph_analyzer.py` | Organizational graph logic |
| `predict_email.py` | CLI-style single-email run |
| `stitch_integration.py` | Optional Stitch / MCP helper text and env checks |

---

## Deployment

### Important: Streamlit and Vercel

**The Streamlit app is not a static site.** It needs a **long-running Python process** and **WebSockets**. [Vercel](https://vercel.com) is built for static frontends, serverless functions, and short-lived requests. **You cannot reliably host the full Streamlit dashboard on Vercel** the same way you host a Next.js app.

You have two practical patterns:

1. **Host the dashboard on a Streamlit-friendly platform** (recommended for the real app).  
2. **Use Vercel for a marketing / landing page** that links to that dashboard (this repo includes a small static page under `web/` for that).

---

### Option A — Streamlit Community Cloud (recommended for the dashboard)

1. Push this repository to GitHub (already: [sayuj5/AeonShield--Phishing-Intent-Analysis-Engine](https://github.com/sayuj5/AeonShield--Phishing-Intent-Analysis-Engine)).  
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud) and sign in with GitHub.  
3. **New app** → select the repo → set **Main file path** to `dashboard.py`.  
4. Choose branch (e.g. `main`) and deploy.  
5. If the build needs extra steps, add a `packages.txt` or `requirements.txt` (this project already has `requirements.txt`).  
6. Upload or generate large artifacts (`*.pkl`, CSVs) per Streamlit Cloud’s file-size limits; commit only what the app needs, or load data from cloud storage if you outgrow limits.

---

### Option B — Deploy the static landing page on Vercel

This gives you a fast global URL on Vercel while the **live analyzer** runs on Streamlit Cloud (or elsewhere).

1. Log in to [vercel.com](https://vercel.com) with GitHub.  
2. **Add New Project** → import `sayuj5/AeonShield--Phishing-Intent-Analysis-Engine`.  
3. Configure the project:  
   - **Framework Preset:** Other  
   - **Root Directory:** `web`  
   - **Build Command:** leave empty (or `echo "no build"`)  
   - **Output Directory:** `.` (default when there is no build)  
4. Deploy. Vercel will serve `web/index.html` as the site entry.  
5. Edit `web/index.html` and set **YOUR_STREAMLIT_CLOUD_URL** (or any hosted Streamlit URL) so the **Launch dashboard** button points to your real app.

To redeploy after changing `web/index.html`, push to `main`; Vercel will rebuild automatically if Git integration is enabled.

---

### Option C — Other hosts for the full Streamlit app

Suitable alternatives include **Render**, **Railway**, **Fly.io**, or a **VPS** with Docker, where you can run:

```bash
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

Use each platform’s docs for Python, port **8501**, and persistent storage for `.pkl` files if you train on the server.

---

## Project recognition

**Final year project — Behala Government Polytechnic**

| Role | Name |
|------|------|
| Backend and integration | Akash Basak |
| ML and stylometry | Abhiraj Kumar Rajak |
| Security analysis and UI | Subhamita Mondal |
| Industry mentor | Sayuj Sur |
| Academic supervisor | Dr. Partha Sarathi Goswami |

---

## Purpose

AeonShield targets sophisticated BEC and impersonation where pure rule-based filters are insufficient, by combining **behavioral and linguistic signals** with **transparent model explanations** and optional **organizational context**.
