# 🥗 Nourish — Indian Diet Planner

> *Personalised nutrition, AI health coaching, meal logging, and weekly planning — built for India.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0-orange)]()

---

## 📌 Table of Contents

1. [About the Project](#about-the-project)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [How It Works](#how-it-works)
5. [Project Structure](#project-structure)
6. [Getting Started](#getting-started)
7. [Deployment](#deployment)
8. [Configuration & Secrets](#configuration--secrets)
9. [Contributing](#contributing)
10. [License](#license)

---

## 🌿 About the Project

**Nourish** is a fully personalised Indian diet planning application built to address a gap that most Western nutrition apps miss — the richness, variety, and nutritional science of traditional Indian food.

### Purpose

Most calorie-tracking apps use Western food databases and Western RDAs. Indian users are left manually searching for "chapati calories" or "dal protein." Nourish solves this by:

- Using **ICMR-NIN** (Indian Council of Medical Research — National Institute of Nutrition) benchmarks instead of USDA values
- Featuring a hand-curated database of **1,448 validated Indian dishes** — from Pesarattu to Sarson Ka Saag
- Incorporating regional cuisine differences across North, South, East, West, Central, and Northeast India
- Supporting common Indian health conditions (Diabetes, PCOS, Hypertension, Anaemia, Thyroid)

### Goals

- Help everyday Indians eat better using familiar, affordable foods
- Provide evidence-based AI health guidance rooted in Indian nutrition science
- Make weekly meal planning, grocery shopping, and nutrient tracking accessible — no nutritionist required
- Integrate modern AI (Claude) to personalise advice at scale

> **Target audience:** Health-conscious Indians aged 18–65, home cooks, fitness enthusiasts, and anyone managing a diet-related health condition.

<!-- [PLACEHOLDER — Add your own project motivation or personal story here] -->

---

## ✨ Key Features

| Tab | Feature | Description |
|-----|---------|-------------|
| 🏠 | **Dashboard** | Nutrition Mandala (3-ring SVG), daily macro progress, smart health insights |
| 📝 | **Meal Logger** | Log meals with serving multiplier, quick-add popular dishes, day health score |
| 🍽️ | **Curated Menu** | 55 traditional dishes, filterable by diet / GI / health goal / ingredient search |
| ⭐ | **Recommendations** | Scoring engine ranks dishes by goal, diet, medical conditions, and region |
| 📅 | **Weekly Planner** | Auto-generate or manually build a full week of healthy meals |
| 🛒 | **Shopping List** | Auto-generated from plan, grouped by grocery category, checkable, exportable |
| 🤖 | **AI Health Advisor** | Health plan, exercise planner, AI chatbot, body analysis, food science articles |
| 🔬 | **Nutrients** | ICMR RDA micronutrient panel, GI reference table, condition-specific guidance |
| 📊 | **Progress** | 7-day calorie chart, achievements system, streak tracker, wellness score |

---

## 🛠 Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **Streamlit** `>=1.32.0` | App framework — UI layout, state management, reactive components |
| **Custom CSS** | Dark saffron design system with CSS variables, card components, typography |
| **Inline SVG** | Nutrition Mandala rings, BMI gauge — rendered server-side in Python |
| **Google Fonts** | Playfair Display (headings), DM Sans (body), Space Mono (labels/tags) |

### Backend / Business Logic

| Technology | Purpose |
|------------|---------|
| **Python** `3.9+` | Core application language |
| **Mifflin-St Jeor equation** | BMR (Basal Metabolic Rate) calculation |
| **TDEE algorithm** | Activity-adjusted calorie target with 5 goal deltas |
| **Macro-split engine** | Goal-based protein / carb / fat ratio calculator |
| **Recommendation scorer** | Rule-based dish ranking (health score, GI, protein, goal alignment) |
| **AI rule engine** | Built-in answer engine for Indian nutrition Q&A (no API needed) |
| **pandas** `>=2.0.0` | GI reference table and food data display |

### AI / External APIs

| Service | Purpose | Required? |
|---------|---------|-----------|
| **Anthropic Claude API** (`claude-sonnet-4-20250514`) | Personalised AI health & diet responses in the chatbot | Optional |
| **Google Fonts CDN** | Typography | Yes (internet required) |

> The app is **fully functional without any API key.** The Anthropic integration upgrades the chatbot from rule-based to full LLM responses.

### Database / Data Layer

| File | Contents |
|------|---------|
| `backend/data/nourish_foods.json` | 1,448 validated Indian dishes — macros, GI, dosha, region, course |
| `backend/data/indian_food.csv` | Raw source CSV with nutritional values |
| `backend/data/Indian_Food_DF.csv` | Enriched dataset with confidence scores and validation flags |

**Key fields per dish:** `name`, `ingredients`, `diet`, `course`, `region`, `dosha`, `kcal`, `protein_g`, `carbs_g`, `fat_g`, `fiber_g`, `gi`, `gl`, `source`, `confidence`, `macro_valid`

### Infrastructure

| Service | Role |
|---------|------|
| **Streamlit Community Cloud** | Free hosting, automatic deploys on `git push` |
| **GitHub** | Source control and CI/CD trigger |

<!-- [PLACEHOLDER — Add any additional infrastructure, e.g. Firebase, Supabase, AWS] -->

---

## ⚙️ How It Works

### Application Flow

```
User opens app
      │
      ▼
┌─────────────────────────────────────┐
│  SIDEBAR — User Profile Setup       │
│  Name · Gender · Age · Weight       │
│  Height · Activity · Goal · Diet    │
│  Region · Health Conditions         │
│  Water Tracker                      │
└──────────────┬──────────────────────┘
               │  Profile feeds into...
               ▼
┌─────────────────────────────────────┐
│  NUTRITION ENGINE                   │
│  BMR (Mifflin-St Jeor)              │
│  × Activity Factor  =  TDEE         │
│  ±  Goal Delta      =  Calorie Goal │
│  →  Macro Split (Protein/Carb/Fat)  │
│  →  BMI + Category                  │
│  →  Water Target (35ml × kg + 200)  │
│  →  Medical Rules (GI cap, sodium)  │
└──────────────┬──────────────────────┘
               │  Targets power all 9 tabs
               ▼
┌──────────┬──────────┬──────────┬────────────┐
│  Meal    │ Curated  │  Recs    │  Weekly    │
│ Logger   │  Menu    │ Engine   │ Planner    │
└────┬─────┴──────────┴──────────┴──────┬─────┘
     │                                  │
     ▼                                  ▼
┌──────────────┐                ┌───────────────┐
│  Shopping    │                │  AI Health    │
│    List      │                │  Advisor      │
│ (12 grocery  │                │ (5 sub-tabs)  │
│  categories) │                └───────────────┘
└──────────────┘
```

### Nutrition Calculation

**BMR Formula (Mifflin-St Jeor):**
```
Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
Female: BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161
```

**TDEE = BMR × Activity Factor**

| Activity Level | Multiplier |
|----------------|-----------|
| Sedentary (desk job) | 1.20 |
| Lightly Active (1–3 days/week) | 1.375 |
| Moderately Active (3–5 days) | 1.55 |
| Very Active (6–7 days) | 1.725 |

**Goal Calorie Deltas:**

| Goal | Adjustment |
|------|-----------|
| Lose Weight | −500 kcal/day |
| Lose Weight (Fast) | −750 kcal/day |
| Maintain Weight | ±0 kcal |
| Gain Muscle | +200 kcal/day |
| Gain Weight | +300 kcal/day |

### Recommendation Engine

Each dish is scored against the user's active profile:
- Base health score (1–10, hand-curated per dish)
- +2 if calorie density matches goal
- +2 if protein >8g and goal is muscle gain
- +1 if GI <55 (for diabetic/PCOS users)
- +2 if dish contains iron-rich ingredients (for anaemia)
- Dishes violating medical rules (GI cap, low-sodium) are filtered out entirely

### AI Health Advisor

Generates a full personalised health plan covering:
- BMI assessment with Indian food-specific recommendations
- Daily meal timing plan matched to goal
- Medical condition guidance (Diabetes, PCOS, Hypertension, Anaemia, Thyroid)
- Micronutrient gap analysis vs ICMR RDA
- Today's calorie/protein gap
- Goal-matched 7-day exercise schedule with calorie burn estimates

Optionally powered by **Claude claude-sonnet-4-20250514** for free-text health Q&A.

---

## 📁 Project Structure

```
nourish-diet-planner/
│
├── app.py                        # Main Streamlit app — all 9 tabs (~1,950 lines)
├── app_backup.py                 # v3 backup (pre-AI-advisor)
├── requirements.txt              # Python dependencies
│
├── .streamlit/
│   └── config.toml               # Dark saffron theme + server config
│
├── backend/
│   ├── core/
│   │   ├── nutrient_engine.py    # Standalone BMR/TDEE/macro calculations
│   │   └── meal_planner.py       # Weekly planner logic
│   └── data/
│       ├── nourish_foods.json    # ★ Primary food database (1,448 dishes)
│       ├── indian_food.csv       # Raw source data
│       └── Indian_Food_DF.csv    # Enriched data with validation scores
│
└── scripts/
    ├── build_database.py         # Rebuilds nourish_foods.json from CSV sources
    └── enrich_indian_foods.py    # Adds GI, dosha, region, ICMR fields
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9 or higher** — [download](https://www.python.org/downloads/)
- `pip` (comes with Python)
- Git — [download](https://git-scm.com/)

### Local Installation

**1. Clone the repository**
```bash
git clone https://github.com/[YOUR_GITHUB_USERNAME]/nourish-diet-planner.git
cd nourish-diet-planner
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

Opens automatically at **http://localhost:8501** ✅

### Optional: Enable Claude AI Chatbot

1. Get a free API key at [console.anthropic.com](https://console.anthropic.com)
2. In the app → **AI Health Advisor → Ask AI → 🔑 Claude AI API Key**
3. Paste your key — used only in your session, never persisted

---

## 🌐 Deployment

### Option 1 — Streamlit Community Cloud (Free, Recommended)

**Step 1: Push to GitHub**
```bash
git init
git add .
git commit -m "feat: initial Nourish v4.0 deployment"
git remote add origin https://github.com/[YOUR_USERNAME]/nourish-diet-planner.git
git branch -M main
git push -u origin main
```

**Step 2: Deploy**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Set: repo → `[YOUR_USERNAME]/nourish-diet-planner` · branch → `main` · file → `app.py`
5. Click **"Deploy!"**

Live URL format:
```
https://[YOUR_USERNAME]-nourish-diet-planner-app-[HASH].streamlit.app
```

### Option 2 — Docker

```bash
# [PLACEHOLDER — Add your Dockerfile if containerising]
# Build
docker build -t nourish .

# Run
docker run -p 8501:8501 nourish
# Access at http://localhost:8501
```

### Option 3 — Other Platforms

<!-- [PLACEHOLDER — Add instructions for Railway, Render, Heroku, or any other platform you use] -->

---

## 🔐 Configuration & Secrets

### Streamlit Cloud Secrets

In Streamlit Cloud → your app → **⋮ → Settings → Secrets**, add:

```toml
# Required for Claude AI chatbot
ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# [PLACEHOLDER — Add any other secrets your deployment needs]
# DATABASE_URL = "postgresql://..."
# FIREBASE_API_KEY = "..."
```

### Local Development

Create `.streamlit/secrets.toml` (this file is in `.gitignore` — never commit it):
```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

Access in code via `st.secrets["ANTHROPIC_API_KEY"]`.

---

## 🤝 Contributing

Contributions are warmly welcome — especially from people who know Indian regional cuisines that are under-represented in nutrition databases!

### Workflow

**1. Fork and clone**
```bash
# Fork on GitHub, then:
git clone https://github.com/[YOUR_FORK]/nourish-diet-planner.git
cd nourish-diet-planner
```

**2. Create a feature branch**
```bash
git checkout -b feature/add-northeast-cuisine
# or
git checkout -b fix/nutrient-calculation-edge-case
```

**3. Commit with clear messages**
```bash
git commit -m "feat: add 30 Assamese dishes to food database"
git commit -m "fix: correct calcium RDA value for post-menopausal women"
git commit -m "docs: expand Bengali regional food section"
```

**4. Push and open a Pull Request**
```bash
git push origin feature/add-northeast-cuisine
# Then open PR on GitHub — describe what you changed and why
```

### Priority Areas for Contribution

- 🌏 **Regional cuisines** — Northeast India (Manipur, Nagaland, Assam), tribal foods, Goan, Kashmiri
- 🌐 **Multilingual UI** — Hindi, Tamil, Telugu, Bengali, Gujarati, Marathi, Kannada
- 📱 **PWA / Offline mode** — Service worker for mobile use without internet
- 📤 **Export features** — PDF meal plan, WhatsApp share, Google Calendar sync
- 🧪 **Tests** — Unit tests for nutrition engine and recommendation scorer
- ♿ **Accessibility** — Screen reader support, keyboard navigation, high-contrast mode
- 🍼 **Special diets** — Pregnancy nutrition, infant/toddler feeding, elderly diet planning
- 📊 **Analytics** — 30-day calorie trend, macro streak heatmap

### Code Guidelines

- Follow **PEP 8** for Python formatting
- All HTML must be built via string concatenation — **no nested f-string quotes** (this caused the v3 rendering bug)
- New dish entries must include: `kcal`, `protein`, `carbs`, `fat`, `fiber`, `gi`, `diet`, `region`, `course`, `ingredients`
- Nutrition values must reference ICMR-NIN or peer-reviewed Indian clinical studies

### Reporting Bugs

Open a GitHub Issue and include:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS
- Any error messages or screenshots

---

## 📊 Data & Methodology

### Food Database

`nourish_foods.json` was built from:
- **ICMR-NIN Indian Food Composition Tables (2017)** — 528 base foods
- **NNMB (National Nutrition Monitoring Bureau)** dietary survey data
- Manual curation of 900+ additional regional dishes with cross-referenced values
- GI values from published clinical studies on South Asian populations

All dishes carry a `confidence` score (0–1) and `macro_valid` boolean flag.

### Nutritional Benchmarks

All RDA values use **ICMR 2020 Indian guidelines** rather than USDA/European standards, as Indian body composition, dietary patterns, and micronutrient requirements differ meaningfully from Western populations.

### Medical Disclaimer

> ⚠️ Nourish is an educational and planning tool, not a medical device. All nutritional information is for general guidance only. Always consult a qualified registered dietitian or doctor for clinical dietary management of any health condition.

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

```
MIT License

Copyright (c) [YEAR] [YOUR NAME OR ORGANISATION]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See the full [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **ICMR-NIN** for the Indian Food Composition Tables that power the nutrition database
- **Streamlit** for making Python data apps genuinely beautiful and deployable
- **Anthropic** for the Claude API powering the AI Health Advisor chatbot
- The Indian nutrition research community whose published work underpins the health guidance in this app

---

<div align="center">

**Built with ❤️ for India's 1.4 billion**

*Nourish v4.0*

<!-- [PLACEHOLDER — Replace with your live app URL once deployed] -->
*🌐 Live App: `https://your-app-url.streamlit.app`*

</div>
