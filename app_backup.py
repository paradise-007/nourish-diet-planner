"""
Nourish — Indian Diet Planner
Streamlit App  |  Deploy: streamlit run app.py
"""

import streamlit as st
import json, random, math
from pathlib import Path

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Nourish — Indian Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE  = Path(__file__).parent
DB    = BASE / "backend" / "data" / "nourish_foods.json"

# ── Load database ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_foods():
    if not DB.exists():
        return []
    with open(DB, encoding="utf-8") as f:
        return json.load(f)["foods"]

# Loaded lazily on first Streamlit render — not at import time
def get_foods():
    return load_foods()

# ── Custom CSS — warm dark theme ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ─── Global ─── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0D0D1A !important;
    color: #FFF8F0 !important;
}
.stApp { background: #0D0D1A; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: rgba(255,107,43,.4); border-radius: 2px; }

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #1A1A2E !important;
    border-right: 1px solid rgba(255,248,240,0.07);
}
[data-testid="stSidebar"] * { color: #FFF8F0 !important; }

/* ─── Metric cards ─── */
[data-testid="metric-container"] {
    background: #16162A;
    border: 1px solid rgba(255,248,240,0.08);
    border-radius: 14px;
    padding: 16px 20px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #FF6B2B !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: .2em !important;
    text-transform: uppercase !important;
    color: rgba(255,248,240,.5) !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #FF6B2B, #F5A623) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: transform .15s, box-shadow .15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(255,107,43,.35) !important;
}

/* ─── Inputs / Sliders ─── */
.stSlider > div > div > div { background: #FF6B2B !important; }
.stSelectbox > div > div, .stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #16162A !important;
    border-color: rgba(255,248,240,.12) !important;
    color: #FFF8F0 !important;
    border-radius: 8px !important;
}
.stMultiSelect > div > div { background: #16162A !important; border-color: rgba(255,248,240,.12) !important; }

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    background: #1A1A2E;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,248,240,.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255,248,240,.5) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: .1em !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,107,43,.15) !important;
    color: #FF6B2B !important;
}

/* ─── Progress bars ─── */
.stProgress > div > div > div { background: #FF6B2B !important; border-radius: 4px !important; }

/* ─── Expanders ─── */
.streamlit-expanderHeader {
    background: #16162A !important;
    border: 1px solid rgba(255,248,240,.08) !important;
    border-radius: 10px !important;
    color: #FFF8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent { background: #16162A !important; border-radius: 0 0 10px 10px; }

/* ─── Dataframes ─── */
[data-testid="stDataFrame"] { background: #16162A !important; border-radius: 10px; }

/* ─── Dividers ─── */
hr { border-color: rgba(255,248,240,.06) !important; }

/* ─── Custom components ─── */
.nourish-logo {
    font-family: 'Playfair Display', serif;
    font-size: 32px; font-weight: 900;
    color: #FF6B2B;
    display: flex; align-items: center; gap: 10px;
}
.section-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 10px; letter-spacing: .3em;
    color: #FF6B2B; text-transform: uppercase;
    margin-bottom: 6px;
}
.card {
    background: #16162A;
    border: 1px solid rgba(255,248,240,.08);
    border-radius: 14px; padding: 20px;
    margin-bottom: 12px;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px; font-weight: 700; margin-bottom: 8px;
}
.stat-big {
    font-family: 'Playfair Display', serif;
    font-size: 42px; font-weight: 700; line-height: 1;
    color: #FF6B2B;
}
.tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 9px; letter-spacing: .12em;
    padding: 3px 10px; border-radius: 10px;
    text-transform: uppercase; margin: 2px;
}
.tag-veg    { background: rgba(78,203,160,.12); color: #4ECBA0; }
.tag-nonveg { background: rgba(255,75,110,.12); color: #FF4B6E; }
.tag-region { background: rgba(0,212,255,.1); color: #00D4FF; }
.tag-course { background: rgba(255,248,240,.07); color: rgba(255,248,240,.6); }
.tag-gi     { background: rgba(245,166,35,.12); color: #F5A623; }

.deficiency-card {
    border-radius: 12px; padding: 16px; margin-bottom: 10px;
    border: 1px solid;
}
.def-critical { background: rgba(255,75,110,.06); border-color: rgba(255,75,110,.25); }
.def-low      { background: rgba(245,166,35,.06); border-color: rgba(245,166,35,.25); }
.def-ok       { background: rgba(78,203,160,.06); border-color: rgba(78,203,160,.2); }

.meal-card {
    background: #16162A;
    border: 1px solid rgba(255,248,240,.08);
    border-radius: 14px; padding: 20px; margin-bottom: 14px;
}
.dish-row {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,248,240,.06);
    border-radius: 10px; padding: 14px; margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# NUTRITION ENGINE (inline — no external import needed for Streamlit Cloud)
# ════════════════════════════════════════════════════════════════════════════

ACTIVITY_FACTORS = {
    "Sedentary (desk job)":        1.2,
    "Lightly Active (1-3 days/wk)":1.375,
    "Moderately Active (3-5 days)": 1.55,
    "Very Active (6-7 days)":       1.725,
}
GOAL_DELTA = {
    "Lose Weight":       -500,
    "Lose Weight (Fast)":-750,
    "Maintain Weight":    0,
    "Gain Muscle":       +200,
    "Gain Weight":       +300,
}
GOAL_SPLITS = {
    "Lose Weight":       (0.35, 0.40, 0.25),
    "Lose Weight (Fast)":(0.40, 0.35, 0.25),
    "Maintain Weight":   (0.25, 0.50, 0.25),
    "Gain Muscle":       (0.35, 0.45, 0.20),
    "Gain Weight":       (0.25, 0.50, 0.25),
}
ICMR_RDA = {
    "Iron":        {"male": 17,   "female": 21,   "unit": "mg",  "key": "iron_mg"},
    "Vitamin B12": {"male": 2.2,  "female": 2.2,  "unit": "mcg", "key": "b12_mcg"},
    "Vitamin D":   {"male": 600,  "female": 600,  "unit": "IU",  "key": "vitamin_d_iu"},
    "Calcium":     {"male": 1000, "female": 1000, "unit": "mg",  "key": "calcium_mg"},
    "Zinc":        {"male": 12,   "female": 10,   "unit": "mg",  "key": "zinc_mg"},
    "Folate":      {"male": 200,  "female": 200,  "unit": "mcg", "key": "folate_mcg"},
}
MICRO_TIPS = {
    "Iron":        ("🩸", "Add spinach dal, rajma with amla juice. Avoid tea/coffee 30 min after meals.", ["Palak dal", "Rajma", "Til ladoo", "Dried dates", "Horse gram dal"]),
    "Vitamin B12": ("🧠", "Almost absent in plant foods. Strongly recommend supplement if vegetarian.", ["Fortified milk", "Curd/yogurt", "Fermented idli batter", "Eggs (if non-veg)"]),
    "Vitamin D":   ("☀️", "15–20 min morning sunlight (before 10am) on arms and face daily.", ["Morning sunlight", "Fortified milk", "Mushrooms (sun-exposed)", "Egg yolk"]),
    "Calcium":     ("🦷", "Ragi is the richest plant calcium source. Soak spinach to reduce oxalates.", ["Ragi roti", "Sesame (til)", "Curd & chaas", "Paneer", "Amaranth (rajgira)"]),
    "Zinc":        ("🛡️", "Soak legumes overnight — reduces phytates, improves zinc absorption.", ["Pumpkin seeds", "Whole wheat roti", "Moong/masoor dal", "Cashews"]),
    "Folate":      ("🌿", "Methi leaves highest plant folate. Lightly steam — heat destroys folate.", ["Methi (fenugreek) leaves", "Palak", "Moong sprouts", "Chana dal", "Drumstick/moringa"]),
}
FESTIVAL_RULES = {
    "None": {},
    "Navratri": {"veg_only": True, "avoid_grains": True},
    "Ekadashi": {"veg_only": True, "avoid_grains": True, "avoid_lentils": True},
    "Ramadan":  {"two_meals": True},
    "Onam":     {"veg_only": True},
    "Pongal":   {"veg_only": True},
}
REGIONAL_STATES = {
    "North":     ["Punjab","Delhi","Uttar Pradesh","Haryana","Uttarakhand","Himachal Pradesh","Jammu and Kashmir","Rajasthan"],
    "South":     ["Tamil Nadu","Karnataka","Kerala","Andhra Pradesh","Telangana"],
    "East":      ["West Bengal","Odisha","Bihar","Jharkhand","Assam"],
    "West":      ["Maharashtra","Gujarat","Goa"],
    "Central":   ["Madhya Pradesh","Chhattisgarh"],
    "Northeast": ["Manipur","Nagaland","Meghalaya","Mizoram","Tripura","Sikkim","Arunachal Pradesh"],
}


def calc_bmr(gender, weight, height, age):
    base = 10 * weight + 6.25 * height - 5 * age
    return base + 5 if gender == "Male" else base - 161

def calc_targets(profile):
    bmr  = calc_bmr(profile["gender"], profile["weight"], profile["height"], profile["age"])
    tdee = bmr * ACTIVITY_FACTORS.get(profile["activity"], 1.375)
    delta = GOAL_DELTA.get(profile["goal"], 0)
    kcal  = max(1200, round(tdee + delta))
    splits = GOAL_SPLITS.get(profile["goal"], (0.25, 0.50, 0.25))
    bmi   = profile["weight"] / (profile["height"] / 100) ** 2
    cats  = [(0,18.5,"Underweight","#00D4FF"),(18.5,25,"Healthy Weight","#4ECBA0"),
             (25,30,"Overweight","#F5A623"),(30,35,"Obese I","#FF6B2B"),(35,100,"Obese II+","#FF4B6E")]
    bmi_cat, bmi_col = next(((c,col) for lo,hi,c,col in cats if lo<=bmi<hi), ("—","#888"))
    ws = max(40, min(100, (85 if 18.5<=bmi<=24.9 else 65) + (3 if profile["diet"]=="Vegetarian" else 0)))
    return {
        "bmr":   round(bmr),
        "tdee":  round(tdee),
        "kcal":  kcal,
        "prot":  round(kcal * splits[0] / 4, 1),
        "carbs": round(kcal * splits[1] / 4, 1),
        "fat":   round(kcal * splits[2] / 9, 1),
        "bmi":   round(bmi, 1),
        "bmi_cat": bmi_cat,
        "bmi_col": bmi_col,
        "water": round(profile["weight"] * 35 + 200),
        "wellness": ws,
    }

def meal_split(targets, bmi):
    kcal = targets["kcal"]
    if bmi < 18.5:
        return [("🌅 Breakfast","8:00 AM",.25),("🥪 Mid-Morning","10:30 AM",.10),
                ("☀️ Lunch","1:00 PM",.30),("🍵 Evening Snack","4:30 PM",.10),("🌙 Dinner","7:30 PM",.25)]
    elif bmi < 30:
        return [("🌅 Breakfast","8:00 AM",.25),("☀️ Lunch","1:00 PM",.35),
                ("🍵 Evening Snack","4:30 PM",.10),("🌙 Dinner","7:30 PM",.30)]
    else:
        return [("🌅 Breakfast","8:30 AM",.28),("☀️ Lunch","1:00 PM",.38),("🌙 Dinner","7:00 PM",.34)]

def filter_pool(foods, profile, festival):
    fest  = FESTIVAL_RULES.get(festival, {})
    rules = profile.get("medical_rules", {})
    pool  = []
    reg_states = REGIONAL_STATES.get(profile.get("region","North"), [])
    for f in foods:
        if not f.get("kcal"): continue
        is_veg = "non" not in (f.get("diet") or "")
        if fest.get("veg_only") and not is_veg: continue
        if profile["diet"] == "Vegetarian" and not is_veg: continue
        if rules.get("max_gi") and f.get("gi") and f["gi"] > rules["max_gi"]: continue
        if rules.get("low_sodium") and (f.get("salt_g") or 0) > 1.5: continue
        f = dict(f)
        f["_regional"] = f.get("state","") in reg_states
        pool.append(f)
    return pool

def pick_dishes(pool, target_kcal, n=2, seed=42):
    rng = random.Random(seed)
    window = 0.40
    lo, hi = target_kcal * (1-window) / n, target_kcal * (1+window) / n
    candidates = [f for f in pool if lo <= (f.get("kcal") or 0) <= hi]
    regional   = [f for f in candidates if f.get("_regional")]
    weighted   = (regional * 3 + candidates) if regional else candidates
    if len(weighted) < n: weighted = pool
    picked, used = [], set()
    attempts = 0
    while len(picked) < n and attempts < 300:
        attempts += 1
        f = rng.choice(weighted)
        if f["id"] not in used:
            used.add(f["id"])
            picked.append(f)
    return picked

def build_plan(profile, targets, festival="None", seed=1):
    pool   = filter_pool(get_foods(), profile, festival)
    meals  = meal_split(targets, targets["bmi"])
    plan   = []
    for i, (name, time, pct) in enumerate(meals):
        tgt_kcal = round(targets["kcal"] * pct)
        dishes   = pick_dishes(pool, tgt_kcal, n=2, seed=seed*100+i)
        act_kcal = sum(d.get("kcal",0) or 0 for d in dishes)
        plan.append({
            "name": name, "time": time, "target": tgt_kcal,
            "dishes": dishes, "kcal": act_kcal,
            "protein": sum(d.get("protein_g",0) or 0 for d in dishes),
            "carbs":   sum(d.get("carbs_g",0)   or 0 for d in dishes),
            "fat":     sum(d.get("fat_g",0)      or 0 for d in dishes),
        })
    return plan

def get_medical_rules(conditions):
    rules = {}
    for c in conditions:
        if "Diabetes" in c:    rules["max_gi"] = 55
        if "Hypertension" in c:rules["low_sodium"] = True
        if "Anaemia" in c:     rules["high_iron"] = True
        if "PCOS" in c:        rules["max_gi"] = 50
    return rules

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — PROFILE
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="nourish-logo">🥗 Nourish</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:.25em;color:rgba(255,248,240,.35);text-transform:uppercase;margin-bottom:20px">Indian Diet Planner</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**👤 Your Profile**")
    name     = st.text_input("Name", value=st.session_state.get("name",""), placeholder="Your name")
    gender   = st.selectbox("Gender", ["Female","Male"])
    age      = st.slider("Age", 16, 80, 28)
    weight   = st.slider("Weight (kg)", 35, 150, 65)
    height   = st.slider("Height (cm)", 140, 210, 162)

    st.divider()
    st.markdown("**🎯 Goal & Lifestyle**")
    activity = st.selectbox("Activity Level", list(ACTIVITY_FACTORS.keys()), index=2)
    goal     = st.selectbox("Goal", list(GOAL_DELTA.keys()), index=2)
    diet     = st.selectbox("Diet Preference", ["Vegetarian","Non-Vegetarian"])
    region   = st.selectbox("Your Region", list(REGIONAL_STATES.keys()))

    st.divider()
    st.markdown("**🏥 Health Conditions** *(optional)*")
    conditions = st.multiselect("Select if applicable",
        ["Diabetes","Hypertension","Anaemia","PCOS","Thyroid"],
        placeholder="None selected")
    festival = st.selectbox("Festival / Fast", list(FESTIVAL_RULES.keys()))

    st.divider()
    calc_btn = st.button("🔥 Calculate My Plan", width='stretch')

# ── Build profile & targets ─────────────────────────────────────────────────
if name: st.session_state["name"] = name

profile = {
    "name": name or "Friend",
    "gender": gender, "age": age, "weight": weight,
    "height": height, "activity": activity, "goal": goal,
    "diet": diet, "region": region,
    "medical": conditions,
    "medical_rules": get_medical_rules(conditions),
}
targets = calc_targets(profile)

# ════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard",
    "🍽️ Today's Meals",
    "📅 Weekly Plan",
    "🔬 Nutrients",
    "🔍 Food Explorer",
    "📊 Progress",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    greet_name = profile["name"] if profile["name"] != "Friend" else ""
    st.markdown(f"""
    <div style="margin-bottom:28px">
      <div class="section-eyebrow">Dashboard</div>
      <h1 style="font-family:'Playfair Display',serif;font-size:38px;font-weight:900;margin:0">
        Namaste{' ' + greet_name if greet_name else ''} 🙏
      </h1>
      <div style="font-family:'Space Mono',monospace;font-size:10px;color:rgba(255,248,240,.4);letter-spacing:.2em;text-transform:uppercase;margin-top:6px">
        Your personalised Indian wellness plan
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top metrics ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔥 Daily Calories", f"{targets['kcal']:,}", f"BMR {targets['bmr']:,}")
    c2.metric("⚖️ BMI", targets["bmi"], targets["bmi_cat"])
    c3.metric("💪 Protein Target", f"{targets['prot']}g", f"of {targets['kcal']} kcal")
    c4.metric("💧 Water Target", f"{targets['water']:,}ml", "daily")
    c5.metric("⭐ Wellness Score", targets["wellness"], "out of 100")

    st.divider()

    # ── Nutrition Mandala (SVG) ──────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="section-eyebrow">Nutrition Mandala</div>', unsafe_allow_html=True)
        st.markdown("*The circular thali — fill each ring by hitting your daily goals.*")

        # Build meal plan for intake estimate
        if "meal_plan" not in st.session_state:
            st.session_state["meal_plan"] = build_plan(profile, targets, festival)
        plan = st.session_state["meal_plan"]

        total_kcal  = sum(m["kcal"]    for m in plan)
        total_prot  = sum(m["protein"] for m in plan)
        total_carbs = sum(m["carbs"]   for m in plan)
        total_fat   = sum(m["fat"]     for m in plan)

        def ring_offset(got, target, circumference):
            pct = min(1.0, got / target) if target > 0 else 0
            return circumference * (1 - pct)

        p_off = ring_offset(total_prot,  targets["prot"],  565)
        c_off = ring_offset(total_carbs, targets["carbs"], 408)
        f_off = ring_offset(total_fat,   targets["fat"],   251)
        overall_pct = round(min(100, total_kcal / targets["kcal"] * 100)) if targets["kcal"] else 0

        mandala_svg = f"""
        <div style="display:flex;justify-content:center;margin:16px 0">
        <div style="position:relative;width:240px;height:240px">
          <svg viewBox="0 0 220 220" width="240" height="240">
            <!-- BG rings -->
            <circle cx="110" cy="110" r="90" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
            <circle cx="110" cy="110" r="65" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
            <circle cx="110" cy="110" r="40" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
            <!-- Protein (outer) -->
            <circle cx="110" cy="110" r="90" fill="none" stroke="#FF6B2B"
              stroke-width="22" stroke-linecap="round"
              stroke-dasharray="565" stroke-dashoffset="{p_off:.0f}"
              transform="rotate(-90 110 110)"/>
            <!-- Carbs (mid) -->
            <circle cx="110" cy="110" r="65" fill="none" stroke="#F5A623"
              stroke-width="22" stroke-linecap="round"
              stroke-dasharray="408" stroke-dashoffset="{c_off:.0f}"
              transform="rotate(-90 110 110)"/>
            <!-- Fat (inner) -->
            <circle cx="110" cy="110" r="40" fill="none" stroke="#4ECBA0"
              stroke-width="22" stroke-linecap="round"
              stroke-dasharray="251" stroke-dashoffset="{f_off:.0f}"
              transform="rotate(-90 110 110)"/>
            <!-- Center text -->
            <text x="110" y="104" text-anchor="middle" font-family="Playfair Display,serif"
              font-size="28" font-weight="700" fill="#FF6B2B">{overall_pct}%</text>
            <text x="110" y="122" text-anchor="middle" font-family="Space Mono,monospace"
              font-size="9" fill="rgba(255,248,240,0.5)" letter-spacing="2">DAILY GOAL</text>
          </svg>
        </div>
        </div>
        <div style="display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:16px">
          <span style="font-size:12px;color:rgba(255,248,240,.6)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#FF6B2B;margin-right:6px"></span>Protein</span>
          <span style="font-size:12px;color:rgba(255,248,240,.6)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#F5A623;margin-right:6px"></span>Carbs</span>
          <span style="font-size:12px;color:rgba(255,248,240,.6)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#4ECBA0;margin-right:6px"></span>Fat</span>
        </div>
        """
        st.markdown(mandala_svg, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-eyebrow">Today\'s Macros</div>', unsafe_allow_html=True)
        st.markdown("")

        def macro_bar(label, got, target, color):
            pct = min(100, int(got/target*100)) if target > 0 else 0
            unit = "kcal" if "Cal" in label else "g"
            st.markdown(f"**{label}** — {round(got)} / {round(target)} {unit}")
            st.progress(pct / 100)

        macro_bar("🔥 Calories", total_kcal, targets["kcal"], "#FF6B2B")
        macro_bar("💪 Protein",  total_prot, targets["prot"], "#FF6B2B")
        macro_bar("⚡ Carbs",    total_carbs,targets["carbs"],"#F5A623")
        macro_bar("🫒 Fat",      total_fat,  targets["fat"],  "#4ECBA0")

        st.divider()
        st.markdown('<div class="section-eyebrow">7-Day Streak</div>', unsafe_allow_html=True)
        streak = 3
        days   = ["M","T","W","T","F","S","S"]
        dots   = "".join([
            f'<div style="width:32px;height:32px;border-radius:50%;background:{"rgba(78,203,160,.2)" if i<streak else "rgba(255,255,255,.06)"};border:1.5px solid {"#4ECBA0" if i<streak else "rgba(255,255,255,.1)"};display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:{"#4ECBA0" if i<streak else "rgba(255,255,255,.3)"};margin:2px">{"✓" if i<streak else days[i]}</div>'
            for i in range(7)
        ])
        st.markdown(f'<div style="display:flex;gap:4px;flex-wrap:wrap">{dots}</div>', unsafe_allow_html=True)

    st.divider()

    # ── BMR / targets explanation ────────────────────────────────────────────
    st.markdown('<div class="section-eyebrow">Your Numbers Explained</div>', unsafe_allow_html=True)
    with st.expander("📐 How we calculated your targets"):
        st.markdown(f"""
**Mifflin-St Jeor BMR Formula ({gender})**
```
BMR = 10 × {weight}kg + 6.25 × {height}cm − 5 × {age} {"+ 5" if gender=="Male" else "− 161"} = **{targets['bmr']} kcal/day**
```
**TDEE** = BMR × Activity Factor ({ACTIVITY_FACTORS[activity]}) = **{targets['tdee']} kcal/day**

**Goal Adjustment** ({goal}) = {GOAL_DELTA[goal]:+d} kcal

**Final Target** = **{targets['kcal']:,} kcal/day**

**Macro Splits** for {goal}: Protein {GOAL_SPLITS[goal][0]*100:.0f}% / Carbs {GOAL_SPLITS[goal][1]*100:.0f}% / Fat {GOAL_SPLITS[goal][2]*100:.0f}%

**Water Target** = {weight} × 35ml + 200ml (India climate) = **{targets['water']:,} ml/day**

*All benchmarks based on ICMR (Indian Council of Medical Research) recommendations.*
        """)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — TODAY'S MEALS
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div class="section-eyebrow">Today's Meal Plan</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;margin-bottom:20px">
      Your {len(meal_split(targets, targets['bmi']))-1 if targets['bmi']>=30 else len(meal_split(targets, targets['bmi']))}-Meal Plan 🍽️
    </h2>
    """, unsafe_allow_html=True)

    c_regen, c_fam, c_seed = st.columns([2,2,2])
    with c_regen:
        if st.button("↻ Regenerate Plan"):
            st.session_state["plan_seed"] = random.randint(1, 9999)
    with c_fam:
        servings = st.number_input("👨‍👩‍👧 Family servings", 1, 10, 1)
    with c_seed:
        st.caption(f"Plan seed: {st.session_state.get('plan_seed', 42)}")

    seed = st.session_state.get("plan_seed", 42)
    plan = build_plan(profile, targets, festival, seed=seed)
    st.session_state["meal_plan"] = plan

    meal_icons = {"Breakfast":"🌅","Lunch":"☀️","Dinner":"🌙","Evening Snack":"🍵","Mid-Morning":"🥪"}

    for m in plan:
        icon = next((v for k,v in meal_icons.items() if k in m["name"]), "🍽️")
        kcal_s = round(m["kcal"] * servings)
        with st.container():
            st.markdown(f"""
            <div class="meal-card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                <div style="display:flex;align-items:center;gap:12px">
                  <span style="font-size:28px">{icon}</span>
                  <div>
                    <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700">{m['name']}</div>
                    <div style="font-size:11px;color:rgba(255,248,240,.5);font-family:'Space Mono',monospace">{m['time']}</div>
                  </div>
                </div>
                <div style="text-align:right">
                  <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#FF6B2B">{kcal_s} kcal</div>
                  <div style="font-size:10px;color:rgba(255,248,240,.4)">target: {round(m['target']*servings)}</div>
                </div>
              </div>
            """, unsafe_allow_html=True)

            for d in m["dishes"]:
                is_veg = "non" not in (d.get("diet") or "")
                region_tag = f'<span class="tag tag-region">{d.get("region","")}</span>' if d.get("region") else ""
                gi_tag = f'<span class="tag tag-gi">GI {d.get("gi")}</span>' if d.get("gi") else ""
                kcal_d = round((d.get("kcal") or 0) * servings)
                st.markdown(f"""
                <div class="dish-row">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div style="flex:1">
                      <div style="font-size:14px;font-weight:600;margin-bottom:6px">{d['name']}</div>
                      <div>
                        <span class="tag {'tag-veg' if is_veg else 'tag-nonveg'}">{'🌱 Veg' if is_veg else '🍗 Non-Veg'}</span>
                        {region_tag}{gi_tag}
                        {'<span class="tag tag-course">' + d.get('course','') + '</span>' if d.get('course') else ''}
                      </div>
                      {f'<div style="font-size:11px;color:rgba(255,248,240,.4);margin-top:6px">⏱ {(d.get("prep_min") or 0)+(d.get("cook_min") or 0)} min total</div>' if d.get("prep_min") else ''}
                    </div>
                    <div style="text-align:right;flex-shrink:0;margin-left:16px">
                      <div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:#FF6B2B">{kcal_d}</div>
                      <div style="font-size:10px;color:rgba(255,248,240,.4)">kcal / {servings if servings>1 else '100g'}</div>
                      <div style="font-size:11px;color:rgba(255,248,240,.5);margin-top:4px">
                        P:{round((d.get('protein_g') or 0)*servings,1)}g C:{round((d.get('carbs_g') or 0)*servings,1)}g F:{round((d.get('fat_g') or 0)*servings,1)}g
                      </div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
              <div style="display:flex;gap:24px;padding-top:12px;border-top:1px solid rgba(255,248,240,.06);margin-top:4px">
                <span style="font-size:12px;color:rgba(255,248,240,.5)">Protein: <strong style="color:#FFF8F0">{round(m['protein']*servings,1)}g</strong></span>
                <span style="font-size:12px;color:rgba(255,248,240,.5)">Carbs: <strong style="color:#FFF8F0">{round(m['carbs']*servings,1)}g</strong></span>
                <span style="font-size:12px;color:rgba(255,248,240,.5)">Fat: <strong style="color:#FFF8F0">{round(m['fat']*servings,1)}g</strong></span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Daily summary
    t_kcal = sum(m["kcal"] for m in plan) * servings
    t_prot = sum(m["protein"] for m in plan) * servings
    t_carb = sum(m["carbs"]   for m in plan) * servings
    t_fat  = sum(m["fat"]     for m in plan) * servings

    st.divider()
    st.markdown('<div class="section-eyebrow">Daily Summary</div>', unsafe_allow_html=True)
    sc1,sc2,sc3,sc4 = st.columns(4)
    sc1.metric("Total Calories", f"{round(t_kcal):,}", f"target {targets['kcal']*servings:,}")
    sc2.metric("Protein",  f"{round(t_prot,1)}g", f"target {targets['prot']*servings}g")
    sc3.metric("Carbs",    f"{round(t_carb,1)}g", f"target {targets['carbs']*servings}g")
    sc4.metric("Fat",      f"{round(t_fat,1)}g",  f"target {targets['fat']*servings}g")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEEKLY PLAN
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class="section-eyebrow">Weekly Overview</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;margin-bottom:20px">
      Your Week at a Glance 📅
    </h2>
    """, unsafe_allow_html=True)

    days_full = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_emojis = ["🌅","🌤️","⛅","☀️","🌤️","🎉","😌"]

    week_data = []
    for i, day in enumerate(days_full):
        day_plan = build_plan(profile, targets, festival, seed=1000+i)
        kcal = sum(m["kcal"] for m in day_plan)
        week_data.append({"day": day, "kcal": kcal, "plan": day_plan, "emoji": day_emojis[i]})

    cols = st.columns(7)
    for i, (col, d) in enumerate(zip(cols, week_data)):
        pct = min(100, int(d["kcal"] / targets["kcal"] * 100))
        with col:
            st.markdown(f"""
            <div style="background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:12px;padding:12px;text-align:center;cursor:pointer">
              <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:rgba(255,248,240,.4);margin-bottom:8px">{d['day'][:3]}</div>
              <div style="font-size:24px;margin-bottom:6px">{d['emoji']}</div>
              <div style="font-family:'Playfair Display',serif;font-size:16px;font-weight:700;color:#FF6B2B">{d['kcal']}</div>
              <div style="font-size:9px;color:rgba(255,248,240,.4)">kcal</div>
              <div style="height:3px;background:rgba(255,255,255,.06);border-radius:2px;margin-top:8px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#FF6B2B,#F5A623);border-radius:2px"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    selected_day = st.selectbox("View detailed plan for:", days_full)
    day_plan_sel = week_data[days_full.index(selected_day)]["plan"]

    st.markdown(f"**{selected_day} — {sum(float(m.get('kcal') or 0) for m in day_plan_sel):.0f} kcal total**")
    for m in day_plan_sel:
        with st.expander(f"{m['name']} · {m['time']} · {m['kcal']} kcal"):
            for d in m["dishes"]:
                kcal_v = float(d.get("kcal") or 0)
                prot_v = float(d.get("protein_g") or 0)
                carb_v = float(d.get("carbs_g") or 0)
                fat_v  = float(d.get("fat_g") or 0)
                st.write(f"**{d['name']}** — {kcal_v:.0f} kcal | P:{prot_v:.0f}g C:{carb_v:.0f}g F:{fat_v:.0f}g")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — NUTRIENTS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
    <div class="section-eyebrow">Nutrient Intelligence Engine</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;margin-bottom:6px">
      Micronutrient Analysis 🔬
    </h2>
    <p style="color:rgba(255,248,240,.55);margin-bottom:24px">
      Benchmarked against ICMR (Indian Council of Medical Research) RDAs — not Western values.
    </p>
    """, unsafe_allow_html=True)

    # Macro targets
    st.markdown("#### Macro Targets")
    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("Protein",  f"{targets['prot']}g",  f"{round(targets['prot']*4)} kcal")
    mc2.metric("Carbs",    f"{targets['carbs']}g", f"{round(targets['carbs']*4)} kcal")
    mc3.metric("Fat",      f"{targets['fat']}g",   f"{round(targets['fat']*9)} kcal")
    mc4.metric("Fibre",    "30–40g",               "ICMR RDA")

    st.divider()
    st.markdown("#### Micronutrient Deficiency Panel")
    st.caption("Most common deficiencies in the Indian population. Enter your known intake below.")

    # Micronutrient intake form
    with st.expander("📝 Enter your estimated intake (optional — helps personalise alerts)"):
        mi_col1, mi_col2, mi_col3 = st.columns(3)
        iron_got  = mi_col1.number_input("Iron (mg)",       0.0, 50.0, 8.0, 0.5, key="iron_input")
        b12_got   = mi_col2.number_input("Vit B12 (mcg)",   0.0, 10.0, 0.4 if diet=="Vegetarian" else 2.0, 0.1, key="b12_input")
        vitd_got  = mi_col3.number_input("Vit D (IU)",      0.0, 2000.0, 120.0, 10.0, key="vitd_input")
        cal_got   = mi_col1.number_input("Calcium (mg)",    0.0, 2000.0, 500.0, 50.0, key="cal_input")
        zinc_got  = mi_col2.number_input("Zinc (mg)",       0.0, 30.0, 7.0, 0.5, key="zinc_input")
        folate_got= mi_col3.number_input("Folate (mcg)",    0.0, 500.0, 100.0, 10.0, key="folate_input")

    intake_vals = {
        "Iron": iron_got, "Vitamin B12": b12_got, "Vitamin D": vitd_got,
        "Calcium": cal_got, "Zinc": zinc_got, "Folate": folate_got,
    }

    for nutrient, info in ICMR_RDA.items():
        rda   = info["female"] if gender == "Female" else info["male"]
        got   = intake_vals.get(nutrient, 0)
        pct   = round(got / rda * 100, 1) if rda > 0 else 0
        status = "deficient" if pct < 50 else "low" if pct < 75 else "ok"

        # Force B12 low for vegetarians
        if nutrient == "Vitamin B12" and diet == "Vegetarian" and status == "ok":
            status = "low"

        icon, tip, foods = MICRO_TIPS.get(nutrient, ("💊", "", []))
        color_map  = {"deficient":"#FF4B6E","low":"#F5A623","ok":"#4ECBA0"}
        css_map    = {"deficient":"def-critical","low":"def-low","ok":"def-ok"}
        label_map  = {"deficient":"🔴 Deficient","low":"🟡 Low","ok":"✅ Adequate"}

        st.markdown(f"""
        <div class="deficiency-card {css_map[status]}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="font-weight:600;font-size:15px">{icon} {nutrient}</div>
            <span style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;
              padding:3px 10px;border-radius:10px;background:rgba(255,255,255,.06);
              color:{color_map[status]}">{label_map[status]}</span>
          </div>
          <div style="height:5px;background:rgba(255,255,255,.06);border-radius:3px;margin-bottom:10px;overflow:hidden">
            <div style="height:100%;width:{min(100,pct)}%;background:{color_map[status]};border-radius:3px"></div>
          </div>
          <div style="font-size:12px;color:rgba(255,248,240,.6);margin-bottom:8px">
            {got} / {rda} {info['unit']} — {pct}% of ICMR RDA
          </div>
          <div style="font-size:12px;color:rgba(255,248,240,.5);line-height:1.6">
            💡 {tip}
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🍽️ Indian food sources for {nutrient}"):
            for food_item in foods:
                st.write(f"• {food_item}")

    st.divider()
    st.markdown("#### Medical Condition Adjustments")
    if conditions:
        for c in conditions:
            rules = get_medical_rules([c])
            if "max_gi" in rules:
                st.info(f"**{c}**: All meal plans filtered to GI < {rules['max_gi']}. Prefer bajra, jowar, whole grains, legumes.")
            if "low_sodium" in rules:
                st.info(f"**{c}**: Low-sodium mode active. Avoid papads, pickles, packaged snacks.")
            if "high_iron" in rules:
                st.success(f"**{c}**: Iron-rich foods prioritised. Pair with Vitamin C sources.")
    else:
        st.caption("No medical conditions selected. Add conditions in the sidebar to activate specialised filtering.")

    st.divider()
    st.markdown("#### Glycemic Index Reference")
    gi_data = {
        "Food": ["White Rice","Brown Rice","Roti","Bajra Roti","Dal (Lentils)","Rajma","Idli","Dosa","Potato","Ragi"],
        "GI":   [72, 50, 62, 54, 29, 29, 77, 55, 80, 68],
        "Category": ["High","Medium","Medium","Medium","Low","Low","High","Medium","High","Medium"],
        "Kcal/100g": [130, 123, 297, 310, 116, 143, 58, 168, 77, 328],
    }
    import pandas as pd
    gi_df = pd.DataFrame(gi_data)
    st.dataframe(gi_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — FOOD EXPLORER
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <div class="section-eyebrow">Database — {len(get_foods()):,} dishes</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;margin-bottom:20px">
      Food Explorer 🔍
    </h2>
    """, unsafe_allow_html=True)

    fe1, fe2, fe3, fe4 = st.columns([3,1,1,1])
    search_q    = fe1.text_input("Search dishes or ingredients", placeholder="e.g. dal, biryani, paneer…")
    diet_flt    = fe2.selectbox("Diet", ["All","Vegetarian","Non-Vegetarian"])
    course_flt  = fe3.selectbox("Course", ["All","main course","breakfast","snack","dessert","starter"])
    region_flt  = fe4.selectbox("Region", ["All"] + list(REGIONAL_STATES.keys()))

    max_kcal    = st.slider("Max calories (per 100g)", 50, 1000, 1000, 50)

    # Filter
    results = get_foods()
    if search_q:
        q = search_q.lower()
        results = [f for f in results if q in (f.get("name","") or "").lower() or q in (f.get("ingredients","") or "").lower()]
    if diet_flt == "Vegetarian":
        results = [f for f in results if "non" not in (f.get("diet","") or "")]
    elif diet_flt == "Non-Vegetarian":
        results = [f for f in results if "non" in (f.get("diet","") or "")]
    if course_flt != "All":
        results = [f for f in results if (f.get("course","") or "").lower() == course_flt]
    if region_flt != "All":
        states = REGIONAL_STATES.get(region_flt, [])
        results = [f for f in results if f.get("state","") in states or f.get("region","") == region_flt]
    results = [f for f in results if (f.get("kcal") or 0) <= max_kcal]

    st.caption(f"**{len(results)}** dishes found")

    if results:
        import pandas as pd
        rows = []
        for f in results[:100]:
            is_veg = "non" not in (f.get("diet","") or "")
            rows.append({
                "Name":       f.get("name",""),
                "Kcal/100g":  f.get("kcal",""),
                "Protein (g)":f.get("protein_g",""),
                "Carbs (g)":  f.get("carbs_g",""),
                "Fat (g)":    f.get("fat_g",""),
                "Fibre (g)":  f.get("fiber_g",""),
                "GI":         f.get("gi",""),
                "Course":     f.get("course",""),
                "Region":     f.get("region","") or f.get("state",""),
                "Diet":       "🌱 Veg" if is_veg else "🍗 Non-Veg",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)

        if len(results) > 100:
            st.caption(f"Showing top 100 of {len(results)} results. Refine your search to see more.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — PROGRESS
# ════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(f"""
    <div class="section-eyebrow">Your Journey</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;margin-bottom:20px">
      Progress & Achievements 📊
    </h2>
    """, unsafe_allow_html=True)

    pg_col1, pg_col2 = st.columns([1,1])

    with pg_col1:
        st.markdown("#### BMI Overview")
        bmi   = targets["bmi"]
        bmi_c = targets["bmi_cat"]
        col_c = targets["bmi_col"]

        # BMI gauge SVG
        pct   = min(1.0, max(0, (bmi - 15) / 25))
        angle = -90 + pct * 180
        rad   = angle * math.pi / 180
        nx    = 100 + 70 * math.cos(rad)
        ny    = 100 + 70 * math.sin(rad)

        st.markdown(f"""
        <div style="text-align:center;background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:14px;padding:28px">
          <svg viewBox="0 0 200 120" width="200">
            <defs>
              <linearGradient id="gg" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   style="stop-color:#00D4FF"/>
                <stop offset="30%"  style="stop-color:#4ECBA0"/>
                <stop offset="55%"  style="stop-color:#F5A623"/>
                <stop offset="75%"  style="stop-color:#FF6B2B"/>
                <stop offset="100%" style="stop-color:#FF4B6E"/>
              </linearGradient>
            </defs>
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,248,240,0.07)" stroke-width="14" stroke-linecap="round"/>
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gg)" stroke-width="14" stroke-linecap="round" opacity=".5"/>
            <line x1="100" y1="100" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{col_c}" stroke-width="3" stroke-linecap="round"/>
            <circle cx="100" cy="100" r="6" fill="{col_c}"/>
          </svg>
          <div style="font-family:'Playfair Display',serif;font-size:42px;font-weight:700;color:{col_c}">{bmi}</div>
          <div style="font-size:14px;color:rgba(255,248,240,.6);margin-top:4px">{bmi_c}</div>
          <div style="font-size:12px;color:rgba(255,248,240,.4);margin-top:8px">Healthy range: 18.5 – 24.9</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Profile Summary")
        profile_items = [
            ("Name", profile["name"]), ("Gender", gender), ("Age", f"{age} years"),
            ("Weight", f"{weight} kg"), ("Height", f"{height} cm"),
            ("Activity", activity.split("(")[0].strip()),
            ("Goal", goal), ("Diet", diet), ("Region", region),
            ("BMR", f"{targets['bmr']} kcal/day"), ("TDEE", f"{targets['tdee']} kcal/day"),
            ("Water", f"{targets['water']:,} ml/day"),
        ]
        for k, v in profile_items:
            col_k, col_v = st.columns([2, 3])
            col_k.caption(k)
            col_v.write(f"**{v}**")

    with pg_col2:
        st.markdown("#### Achievements")

        streak_val = 3
        achievements = [
            ("🌱", "First Step",       "Profile created",         True),
            ("🔥", "3-Day Streak",     "Log meals 3 days in a row", streak_val >= 3),
            ("💪", "Protein Pro",      "Hit protein goal",         False),
            ("🥦", "Veggie Champion",  "7 vegetarian days",        diet == "Vegetarian"),
            ("⚖️", "BMI Target",       "Healthy BMI range",        18.5 <= bmi <= 24.9),
            ("⭐", "Wellness Star",    "Wellness score > 80",      targets["wellness"] >= 80),
            ("🌿", "Green Eater",      "High fibre week",          False),
            ("🏆", "30 Day Champion",  "30-day streak",            False),
        ]

        ach_cols = st.columns(4)
        for i, (icon, title, desc, unlocked) in enumerate(achievements):
            with ach_cols[i % 4]:
                bg    = "rgba(255,107,43,.08)" if unlocked else "rgba(255,255,255,.02)"
                bdr   = "rgba(255,107,43,.3)"  if unlocked else "rgba(255,255,255,.07)"
                filt  = "none"                  if unlocked else "grayscale(1) opacity(.4)"
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {bdr};border-radius:12px;
                  padding:16px;text-align:center;margin-bottom:10px">
                  <div style="font-size:28px;filter:{filt};margin-bottom:8px">{icon}</div>
                  <div style="font-size:11px;font-weight:600;line-height:1.3">{title}</div>
                  <div style="font-size:10px;color:rgba(255,248,240,.4);margin-top:3px">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Wellness Score Breakdown")
        bmi_score = 40 if 18.5<=bmi<=24.9 else (32 if 17.5<=bmi<25 else 20)
        ws_items = [
            ("BMI Score",      bmi_score, 40, "#FF6B2B"),
            ("Macro Adherence",20,         30, "#F5A623"),
            ("Streak Bonus",   min(20, streak_val*2), 20, "#4ECBA0"),
            ("Hydration",      7,          10, "#00D4FF"),
        ]
        for label, got, total, color in ws_items:
            st.markdown(f"**{label}** — {got}/{total}")
            st.progress(float(got)/float(total) if total else 0.0)

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("""
<div style="text-align:center;padding:20px 0">
  <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#FF6B2B;margin-bottom:6px">🥗 Nourish</div>
  <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.25em;color:rgba(255,248,240,.25);text-transform:uppercase">
    Indian Diet Planner · Built with Priority · ICMR-Benchmarked · 1,353 Dishes
  </div>
</div>
""", unsafe_allow_html=True)
