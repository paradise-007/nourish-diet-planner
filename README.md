# 🥗 Nourish — Streamlit Deployment

## Deploy to Streamlit Cloud (Free, 5 minutes)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Nourish diet planner"
git remote add origin https://github.com/YOUR_USERNAME/nourish
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo → Branch: `main` → Main file: `app.py`
5. Click **Deploy!**

Your app will be live at: `https://YOUR_USERNAME-nourish-app.streamlit.app`

---

## Run Locally
```bash
pip install streamlit pandas
streamlit run app.py
```
Opens at: **http://localhost:8501**

---

## Project Files
```
nourish_streamlit/
├── app.py                    ← Main Streamlit app (all 5 priorities)
├── requirements.txt          ← streamlit + pandas only
├── .streamlit/
│   └── config.toml          ← Dark theme config
├── backend/
│   ├── core/
│   │   ├── nutrient_engine.py
│   │   └── meal_planner.py
│   └── data/
│       ├── nourish_foods.json   ← 1,353 validated dishes (pre-built)
│       ├── indian_food.csv
│       └── Indian_Food_DF.csv
└── scripts/
    └── build_database.py    ← Rebuild database if needed
```

---

## Features
- **Dashboard** — Nutrition Mandala (SVG), macro progress, streak tracker
- **Today's Meals** — Personalised plan, family scaling, regenerate
- **Weekly Plan** — 7-day overview, editorial day columns
- **Nutrients** — Micronutrient deficiency panel (ICMR RDA), GI table
- **Food Explorer** — Search 1,353 dishes with filters
- **Progress** — BMI gauge, achievements, wellness score breakdown
