# 🚀 PANTERRA AI v2.0

> Enterprise-grade AI-Powered Trading Intelligence Platform

PANTERRA AI is a modern AI-powered trading platform built with **FastAPI**, **Next.js**, and **Artificial Intelligence** to provide advanced market analytics, option chain intelligence, portfolio management, risk analysis, and real-time trading insights.

The platform combines quantitative finance, technical analysis, machine learning, and institutional market analytics into a single professional trading workspace.

---

# ✨ Key Features

## 🤖 Artificial Intelligence
- AI Trade Recommendations
- AI Market Analysis
- AI Options Analysis
- AI Confidence Score
- AI Trade Explanation
- AI Risk Assessment

## 📈 Market Intelligence
- Live Market Dashboard
- Market Regime Detection
- Institutional Flow Analysis
- Volatility Engine
- Probability Engine
- Market Sentiment Analysis

## 📊 Options Analytics
- Live Option Chain
- Greeks Analysis
- IV Analysis
- Open Interest Analysis
- PCR Analysis
- AI Strike Ranking

## 💼 Portfolio Management
- Portfolio Analytics
- Performance Dashboard
- Position Management
- Risk Management
- Trade Journal
- Paper Trading

## 📉 Analytics
- Daily Performance
- Weekly Performance
- Monthly Performance
- AI Accuracy Reports
- Strategy Analytics
- Risk & Reward Analytics

## ⚙ Administration
- Admin Dashboard
- User Management
- Authentication
- Role-Based Access Control
- API Monitoring
- System Monitoring

---

# 🏗 Architecture

```
┌───────────────────────────────┐
│        Next.js Frontend       │
└───────────────┬───────────────┘
                │ REST API
                ▼
┌───────────────────────────────┐
│        FastAPI Backend        │
└───────────────┬───────────────┘
                │
 ┌──────────────┼──────────────┐
 │              │              │
 ▼              ▼              ▼
AI Engine   PostgreSQL   Market Data
```

---

# 🛠 Technology Stack

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- TanStack Query
- Zustand
- React Hook Form
- Axios
- Recharts
- TradingView Lightweight Charts

---

## Backend

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Docker
- Render

---

## AI Engines

- AI Trade Recommendation
- AI Options Engine
- Option Chain Analytics
- Greeks Engine
- Volatility Engine
- Probability Engine
- Market Regime Engine
- Institutional Flow Engine
- Portfolio Analytics
- Risk Management Engine

---

# 📁 Project Roadmap

| Module | Description | Status |
|---------|-------------|--------|
| Module 1 | Foundation (Setup, Authentication, Layout, Dashboard) | ✅ Completed |
| Module 2 | Live Markets & API Integration | 🚧 In Progress |
| Module 3 | Charts, Scanner & AI Signals | ⏳ Planned |
| Module 4 | Portfolio, Paper Trading & Journal | ⏳ Planned |
| Module 5 | Option Chain, Greeks & Analytics | ⏳ Planned |
| Module 6 | Admin Dashboard & Reports | ⏳ Planned |

---

# 🚀 Quick Start

```bash
git clone <repository-url>

cd panterra-ai

npm install

cp .env.example .env.local

npm run dev
```

Open:

```
http://localhost:3000
```

---

# 🔗 Backend Configuration

Update your environment file:

```env
NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com
```

---

# 🌐 CORS Configuration

Enable CORS in your FastAPI application.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# 🔌 API Integration

The frontend consumes the existing FastAPI backend.

Current integrations include:

- Authentication
- Portfolio
- Watchlist
- Market Data
- AI Dashboard
- AI Signals
- AI Recommendation
- Prediction Engine
- Risk Manager
- Scanner
- Paper Trading
- Trade Journal
- Performance Analytics
- Financial Data
- Live Option Chain
- Option Prices
- Option Greeks
- Option Scoring
- AI Options
- Volatility Engine
- Probability Engine
- Market Regime
- Institutional Flow
- Trade Recommendation

---

# 📌 Development Status

- Backend Development: **90% Complete**
- Frontend Development: **In Progress**
- API Integration: **In Progress**
- Testing: **Pending**
- Production Deployment: **Planned**

---

# 📄 License

© 2026 PANTERRA AI. All Rights Reserved.