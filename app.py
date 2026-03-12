"""
Nourish — Indian Diet Planner  v4.0
Fixes: HTML rendering bug (nested f-string quotes in st.markdown)
New:   AI Health Advisor tab powered by Claude API (via Anthropic)
       Exercise Planner, Nutrient AI, Meal AI using free/built-in intelligence
Run:   streamlit run app.py
"""

import streamlit as st
import json, random, math, datetime, re
from pathlib import Path
from collections import defaultdict

# ── Optional Anthropic import ──────────────────────────────────────────────
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

st.set_page_config(
    page_title="Nourish — Indian Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
DB   = BASE / "backend" / "data" / "nourish_foods.json"

@st.cache_data(show_spinner=False)
def load_foods():
    if not DB.exists():
        return []
    with open(DB, encoding="utf-8") as f:
        return json.load(f)["foods"]

def get_foods():
    return load_foods()

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');
:root{--saffron:#FF6B2B;--turmeric:#F5A623;--mint:#4ECBA0;--rose:#FF4B6E;--sky:#00D4FF;--ink:#0D0D1A;--card:#16162A;--border:rgba(255,248,240,.08);--text:#FFF8F0;--muted:rgba(255,248,240,.45)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background:#0D0D1A!important;color:#FFF8F0!important}
.stApp{background:#0D0D1A}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-thumb{background:rgba(255,107,43,.4);border-radius:2px}
[data-testid="stSidebar"]{background:#1A1A2E!important;border-right:1px solid rgba(255,248,240,.07)}
[data-testid="stSidebar"] *{color:#FFF8F0!important}
[data-testid="metric-container"]{background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:14px;padding:16px 20px!important}
[data-testid="stMetricValue"]{font-family:'Playfair Display',serif!important;font-size:26px!important;font-weight:700!important;color:#FF6B2B!important}
[data-testid="stMetricLabel"]{font-family:'Space Mono',monospace!important;font-size:10px!important;letter-spacing:.2em!important;text-transform:uppercase!important;color:rgba(255,248,240,.5)!important}
.stButton>button{background:linear-gradient(135deg,#FF6B2B,#F5A623)!important;color:#000!important;font-weight:700!important;border:none!important;border-radius:10px!important;padding:10px 28px!important;transition:transform .15s,box-shadow .15s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(255,107,43,.35)!important}
.stSlider>div>div>div{background:#FF6B2B!important}
.stSelectbox>div>div,.stTextInput>div>div>input,.stNumberInput>div>div>input{background:#16162A!important;border-color:rgba(255,248,240,.12)!important;color:#FFF8F0!important;border-radius:8px!important}
.stMultiSelect>div>div{background:#16162A!important;border-color:rgba(255,248,240,.12)!important}
.stTextArea>div>textarea{background:#16162A!important;border-color:rgba(255,248,240,.12)!important;color:#FFF8F0!important;border-radius:8px!important}
.stTabs [data-baseweb="tab-list"]{background:#1A1A2E;border-radius:10px;padding:4px;gap:2px;border:1px solid rgba(255,248,240,.06)}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:rgba(255,248,240,.5)!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:9px!important;letter-spacing:.08em!important}
.stTabs [aria-selected="true"]{background:rgba(255,107,43,.15)!important;color:#FF6B2B!important}
.stProgress>div>div>div{background:#FF6B2B!important;border-radius:4px!important}
.streamlit-expanderHeader{background:#16162A!important;border:1px solid rgba(255,248,240,.08)!important;border-radius:10px!important;color:#FFF8F0!important}
.streamlit-expanderContent{background:#16162A!important;border-radius:0 0 10px 10px}
hr{border-color:rgba(255,248,240,.06)!important}
/* Custom classes */
.logo{font-family:'Playfair Display',serif;font-size:32px;font-weight:900;color:#FF6B2B}
.eyebrow{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.3em;color:#FF6B2B;text-transform:uppercase;margin-bottom:6px}
.h1{font-family:'Playfair Display',serif;font-size:34px;font-weight:900;margin:0;line-height:1.1}
.card{background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:14px;padding:20px;margin-bottom:12px}
.dish-card{background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:12px;padding:14px;margin-bottom:8px}
/* Tags - rendered safely via helper functions */
.tag{display:inline-block;font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;padding:3px 9px;border-radius:10px;text-transform:uppercase;margin:2px}
.tv{background:rgba(78,203,160,.12);color:#4ECBA0}
.tnv{background:rgba(255,75,110,.12);color:#FF4B6E}
.tgi-lo{background:rgba(78,203,160,.12);color:#4ECBA0}
.tgi-md{background:rgba(245,166,35,.12);color:#F5A623}
.tgi-hi{background:rgba(255,75,110,.12);color:#FF4B6E}
.tc{background:rgba(255,248,240,.07);color:rgba(255,248,240,.6)}
/* Macro pills */
.mp{display:inline-flex;align-items:center;padding:4px 10px;border-radius:16px;font-size:11px;font-weight:600;margin:2px}
.mp-k{background:rgba(0,212,255,.1);color:#00D4FF}
.mp-p{background:rgba(255,107,43,.12);color:#FF6B2B}
.mp-c{background:rgba(245,166,35,.12);color:#F5A623}
.mp-f{background:rgba(78,203,160,.12);color:#4ECBA0}
/* Log rows */
.lr{background:rgba(255,107,43,.05);border:1px solid rgba(255,107,43,.15);border-radius:10px;padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
/* Alert boxes */
.ab{border-radius:10px;padding:12px 16px;margin-bottom:8px;font-size:13px;line-height:1.6}
.ab-w{background:rgba(245,166,35,.08);border:1px solid rgba(245,166,35,.25)}
.ab-g{background:rgba(78,203,160,.08);border:1px solid rgba(78,203,160,.2)}
.ab-i{background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.2)}
.ab-d{background:rgba(255,75,110,.08);border:1px solid rgba(255,75,110,.25)}
/* Recommendation card */
.rc{background:linear-gradient(135deg,rgba(255,107,43,.08),rgba(245,166,35,.05));border:1px solid rgba(255,107,43,.2);border-radius:14px;padding:16px;margin-bottom:10px;height:100%}
/* AI response */
.ai-box{background:linear-gradient(135deg,#16162A,#1e1e38);border:1px solid rgba(255,107,43,.25);border-radius:14px;padding:20px;margin-top:16px;line-height:1.8;font-size:13px}
.ai-section{margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,248,240,.06)}
.ai-section:last-child{border-bottom:none;margin-bottom:0}
.health-score{font-family:'Playfair Display',serif;font-size:52px;font-weight:900;line-height:1}
/* Exercise card */
.ex-card{background:#1e1e38;border:1px solid rgba(0,212,255,.15);border-radius:12px;padding:16px;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAFE HTML HELPERS  (fixes the nested-quotes f-string bug)
# ══════════════════════════════════════════════════════════════════════════════
def veg_tag(is_veg: bool) -> str:
    if is_veg:
        return '<span class="tag tv">🌱 Veg</span>'
    return '<span class="tag tnv">🍗 Non-Veg</span>'

def gi_tag(gi) -> str:
    if gi is None:
        return ""
    if gi < 55:
        return f'<span class="tag tgi-lo">GI {gi} ✓</span>'
    if gi < 70:
        return f'<span class="tag tgi-md">GI {gi}</span>'
    return f'<span class="tag tgi-hi">GI {gi} ⚠</span>'

def course_tag(text: str) -> str:
    return f'<span class="tag tc">{text}</span>'

def reason_badge(text: str) -> str:
    return f'<span style="background:rgba(78,203,160,.1);color:#4ECBA0;font-size:9px;padding:2px 8px;border-radius:8px;font-family:Space Mono,monospace">{text}</span>'

def mp(cls: str, val: str) -> str:
    return f'<span class="mp mp-{cls}">{val}</span>'

def health_color(score: int) -> str:
    if score >= 9: return "#4ECBA0"
    if score >= 7: return "#F5A623"
    return "#FF4B6E"

def alert(kind: str, text: str) -> str:
    cls = {"warn":"ab-w","good":"ab-g","info":"ab-i","danger":"ab-d"}.get(kind,"ab-i")
    return f'<div class="ab {cls}">{text}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# NUTRITION ENGINE
# ══════════════════════════════════════════════════════════════════════════════
ACTIVITY_FACTORS = {
    "Sedentary (desk job)": 1.20,
    "Lightly Active (1-3 days/wk)": 1.375,
    "Moderately Active (3-5 days)": 1.55,
    "Very Active (6-7 days)": 1.725,
}
GOAL_DELTA  = {
    "Lose Weight": -500, "Lose Weight (Fast)": -750,
    "Maintain Weight": 0, "Gain Muscle": 200, "Gain Weight": 300,
}
GOAL_SPLITS = {
    "Lose Weight":        (0.35, 0.40, 0.25),
    "Lose Weight (Fast)": (0.40, 0.35, 0.25),
    "Maintain Weight":    (0.25, 0.50, 0.25),
    "Gain Muscle":        (0.35, 0.45, 0.20),
    "Gain Weight":        (0.25, 0.50, 0.25),
}
ICMR_RDA = {
    "Iron":        {"male": 17,   "female": 21,   "unit": "mg"},
    "Vitamin B12": {"male": 2.2,  "female": 2.2,  "unit": "mcg"},
    "Vitamin D":   {"male": 600,  "female": 600,  "unit": "IU"},
    "Calcium":     {"male": 1000, "female": 1000, "unit": "mg"},
    "Zinc":        {"male": 12,   "female": 10,   "unit": "mg"},
    "Folate":      {"male": 200,  "female": 200,  "unit": "mcg"},
}
MICRO_TIPS = {
    "Iron":        ("🩸","Pair with Vitamin C (amla, lemon). Avoid tea/coffee 30 min after meals.",["Palak dal","Rajma","Til ladoo","Dried dates","Horse gram","Ragi"]),
    "Vitamin B12": ("🧠","Almost absent in plant foods. Supplement if vegetarian.",["Fortified milk","Curd/chaas","Fermented batter","Eggs","Paneer"]),
    "Vitamin D":   ("☀️","15–20 min morning sunlight before 10am daily.",["Morning sunlight","Fortified milk","Mushrooms (sun-exposed)","Egg yolk"]),
    "Calcium":     ("🦷","Ragi is India's richest plant calcium. Soak spinach to reduce oxalates.",["Ragi roti","Sesame (til)","Curd","Paneer","Amaranth","Drumstick leaves"]),
    "Zinc":        ("🛡️","Soak legumes overnight to reduce phytates.",["Pumpkin seeds","Whole wheat roti","Moong/masoor dal","Cashews"]),
    "Folate":      ("🌿","Methi leaves richest Indian plant folate. Lightly steam only.",["Methi leaves","Palak","Moong sprouts","Chana dal","Moringa"]),
}
REGIONAL_STATES = {
    "North":     ["Punjab","Delhi","UP","Haryana","Rajasthan","J&K","Uttarakhand"],
    "South":     ["Tamil Nadu","Karnataka","Kerala","Andhra Pradesh","Telangana"],
    "East":      ["West Bengal","Odisha","Bihar","Jharkhand","Assam"],
    "West":      ["Maharashtra","Gujarat","Goa"],
    "Central":   ["Madhya Pradesh","Chhattisgarh"],
    "Northeast": ["Manipur","Nagaland","Meghalaya","Mizoram","Tripura","Sikkim"],
}

# ══════════════════════════════════════════════════════════════════════════════
# CURATED MENU  (55 dishes)
# ══════════════════════════════════════════════════════════════════════════════
CURATED_MENU = {
    "🌅 Breakfast": [
        {"name":"Idli + Sambar","kcal":116,"protein":5.2,"carbs":22.8,"fat":0.8,"fiber":3.2,"diet":"vegetarian","gi":54,"healthy_score":9,"tags":["South Indian","Low Fat","Probiotic"],"ingredients":["Rice","Urad Dal","Toor Dal","Tamarind","Vegetables","Mustard","Curry Leaves"]},
        {"name":"Masala Dosa","kcal":198,"protein":5.2,"carbs":34.2,"fat":5.8,"fiber":2.4,"diet":"vegetarian","gi":60,"healthy_score":7,"tags":["South Indian","Classic"],"ingredients":["Rice","Urad Dal","Potato","Green Chilli","Mustard","Oil","Spices"]},
        {"name":"Poha","kcal":108,"protein":2.8,"carbs":22.4,"fat":1.4,"fiber":0.8,"diet":"vegetarian","gi":55,"healthy_score":8,"tags":["Central India","Light","Quick"],"ingredients":["Flattened Rice","Onion","Mustard","Curry Leaves","Peanuts","Turmeric","Lemon"]},
        {"name":"Upma","kcal":128,"protein":3.8,"carbs":22.4,"fat":3.2,"fiber":1.4,"diet":"vegetarian","gi":50,"healthy_score":8,"tags":["South Indian","Filling"],"ingredients":["Semolina","Onion","Green Chilli","Mustard","Cashew","Curry Leaves","Oil"]},
        {"name":"Aloo Paratha + Curd","kcal":342,"protein":9.2,"carbs":52.4,"fat":11.2,"fiber":3.6,"diet":"vegetarian","gi":63,"healthy_score":6,"tags":["Punjab","Hearty"],"ingredients":["Whole Wheat Flour","Potato","Green Chilli","Coriander","Ghee","Curd","Spices"]},
        {"name":"Besan Chilla","kcal":148,"protein":7.8,"carbs":16.4,"fat":5.2,"fiber":3.2,"diet":"vegetarian","gi":30,"healthy_score":9,"tags":["High Protein","Low GI","Quick"],"ingredients":["Chickpea Flour","Onion","Green Chilli","Coriander","Tomato","Oil","Spices"]},
        {"name":"Moong Dal Chilla","kcal":138,"protein":8.4,"carbs":14.8,"fat":4.4,"fiber":3.6,"diet":"vegetarian","gi":28,"healthy_score":9,"tags":["High Protein","Low GI","Healthy"],"ingredients":["Yellow Moong Dal","Ginger","Green Chilli","Onion","Coriander","Oil"]},
        {"name":"Daliya Porridge","kcal":102,"protein":3.8,"carbs":18.4,"fat":1.2,"fiber":2.8,"diet":"vegetarian","gi":41,"healthy_score":10,"tags":["Weight Loss","High Fiber","Low GI"],"ingredients":["Broken Wheat","Milk","Jaggery","Cardamom"]},
        {"name":"Pongal (Ven Pongal)","kcal":138,"protein":4.8,"carbs":24.2,"fat":3.2,"fiber":1.6,"diet":"vegetarian","gi":50,"healthy_score":8,"tags":["Tamil Nadu","Easy Digest"],"ingredients":["Rice","Moong Dal","Ghee","Ginger","Curry Leaves","Black Pepper","Cumin"]},
        {"name":"Pesarattu","kcal":148,"protein":7.2,"carbs":22.4,"fat":3.2,"fiber":2.8,"diet":"vegetarian","gi":38,"healthy_score":9,"tags":["Andhra","High Protein"],"ingredients":["Green Moong Dal","Ginger","Green Chilli","Cumin","Onion","Oil"]},
        {"name":"Ragi Porridge","kcal":112,"protein":2.8,"carbs":22.4,"fat":1.2,"fiber":2.2,"diet":"vegetarian","gi":68,"healthy_score":8,"tags":["Karnataka","Calcium Rich"],"ingredients":["Finger Millet Flour","Water","Jaggery","Cardamom"]},
        {"name":"Egg Bhurji","kcal":158,"protein":12.4,"carbs":4.2,"fat":10.4,"fiber":0.8,"diet":"non-vegetarian","gi":20,"healthy_score":8,"tags":["High Protein","Quick","Low Carb"],"ingredients":["Eggs","Onion","Tomato","Green Chilli","Coriander","Oil","Spices"]},
        {"name":"Methi Paratha","kcal":318,"protein":9.2,"carbs":49.8,"fat":10.8,"fiber":4.1,"diet":"vegetarian","gi":58,"healthy_score":7,"tags":["North India","Iron Rich"],"ingredients":["Whole Wheat Flour","Fenugreek Leaves","Ghee","Spices","Salt"]},
        {"name":"Rava Idli","kcal":118,"protein":3.8,"carbs":21.4,"fat":2.2,"fiber":0.8,"diet":"vegetarian","gi":65,"healthy_score":7,"tags":["South Indian","Quick"],"ingredients":["Semolina","Yogurt","Cashew","Mustard","Curry Leaves","Eno"]},
        {"name":"Sabudana Khichdi","kcal":198,"protein":2.4,"carbs":40.8,"fat":4.2,"fiber":0.8,"diet":"vegetarian","gi":75,"healthy_score":5,"tags":["Fasting","Maharashtra"],"ingredients":["Sago","Potato","Peanuts","Green Chilli","Cumin","Oil"]},
    ],
    "☀️ Lunch": [
        {"name":"Dal Tadka + Roti","kcal":238,"protein":12.4,"carbs":38.6,"fat":4.2,"fiber":5.8,"diet":"vegetarian","gi":35,"healthy_score":9,"tags":["North India","High Protein","Balanced"],"ingredients":["Toor Dal","Tomato","Onion","Garlic","Ghee","Whole Wheat Flour","Turmeric","Cumin"]},
        {"name":"Rajma Chawal","kcal":278,"protein":14.2,"carbs":44.8,"fat":3.6,"fiber":8.0,"diet":"vegetarian","gi":40,"healthy_score":9,"tags":["Punjab","High Protein","Iron Rich"],"ingredients":["Kidney Beans","Basmati Rice","Tomato","Onion","Garlic","Ginger","Spices","Ghee"]},
        {"name":"Palak Paneer + Roti","kcal":386,"protein":16.2,"carbs":34.6,"fat":17.8,"fiber":4.8,"diet":"vegetarian","gi":36,"healthy_score":8,"tags":["North India","Iron Rich","Calcium"],"ingredients":["Spinach","Paneer","Onion","Tomato","Cream","Garlic","Spices","Whole Wheat Flour"]},
        {"name":"Sambar Rice","kcal":178,"protein":6.8,"carbs":31.4,"fat":2.2,"fiber":5.8,"diet":"vegetarian","gi":50,"healthy_score":9,"tags":["Tamil Nadu","High Fiber"],"ingredients":["Rice","Toor Dal","Tamarind","Mixed Vegetables","Sambar Powder","Mustard","Curry Leaves"]},
        {"name":"Chole + Bhatura","kcal":538,"protein":16.8,"carbs":72.2,"fat":18.2,"fiber":9.4,"diet":"vegetarian","gi":48,"healthy_score":6,"tags":["Punjab","Indulgent"],"ingredients":["Chickpeas","Refined Flour","Yogurt","Chole Masala","Onion","Oil","Tamarind"]},
        {"name":"Vegetable Biryani","kcal":192,"protein":4.8,"carbs":35.2,"fat":4.1,"fiber":2.8,"diet":"vegetarian","gi":60,"healthy_score":7,"tags":["Hyderabad","Festive"],"ingredients":["Basmati Rice","Mixed Vegetables","Ghee","Whole Spices","Saffron","Fried Onion","Yogurt"]},
        {"name":"Chicken Biryani","kcal":220,"protein":12.4,"carbs":30.2,"fat":6.2,"fiber":1.5,"diet":"non-vegetarian","gi":62,"healthy_score":7,"tags":["Hyderabad","High Protein"],"ingredients":["Basmati Rice","Chicken","Yogurt","Whole Spices","Saffron","Fried Onion","Ghee"]},
        {"name":"Dal Makhani + Rice","kcal":272,"protein":13.4,"carbs":38.8,"fat":7.8,"fiber":6.2,"diet":"vegetarian","gi":36,"healthy_score":8,"tags":["Punjab","Protein Rich"],"ingredients":["Black Lentils","Kidney Beans","Butter","Cream","Tomato","Spices","Rice"]},
        {"name":"Khichdi","kcal":135,"protein":5.8,"carbs":23.4,"fat":2.4,"fiber":2.0,"diet":"vegetarian","gi":55,"healthy_score":9,"tags":["Gujarat","Easy Digest"],"ingredients":["Rice","Moong Dal","Ghee","Turmeric","Cumin","Salt"]},
        {"name":"Bisi Bele Bath","kcal":148,"protein":5.6,"carbs":24.2,"fat":3.2,"fiber":3.4,"diet":"vegetarian","gi":56,"healthy_score":8,"tags":["Karnataka","Complete Meal"],"ingredients":["Rice","Toor Dal","Mixed Vegetables","Ghee","Bisi Bele Bath Powder","Tamarind"]},
        {"name":"Butter Chicken + Naan","kcal":508,"protein":23.8,"carbs":38.6,"fat":22.4,"fiber":2.4,"diet":"non-vegetarian","gi":50,"healthy_score":6,"tags":["Punjab","Rich"],"ingredients":["Chicken","Butter","Cream","Tomato","Cashew","Naan","Whole Spices","Kasuri Methi"]},
        {"name":"Fish Curry + Rice","kcal":278,"protein":22.4,"carbs":28.4,"fat":8.4,"fiber":1.6,"diet":"non-vegetarian","gi":55,"healthy_score":9,"tags":["Kerala","Omega-3"],"ingredients":["Fish","Coconut Milk","Kokum","Red Chilli","Spices","Rice","Coconut Oil"]},
        {"name":"Kadhi Pakora + Rice","kcal":248,"protein":6.8,"carbs":34.8,"fat":8.4,"fiber":2.6,"diet":"vegetarian","gi":45,"healthy_score":7,"tags":["Punjab","Probiotic"],"ingredients":["Yogurt","Besan","Onion","Mustard","Curry Leaves","Rice","Oil"]},
        {"name":"Aloo Gobi + Roti","kcal":296,"protein":8.2,"carbs":44.6,"fat":7.4,"fiber":5.6,"diet":"vegetarian","gi":60,"healthy_score":7,"tags":["North India","Classic"],"ingredients":["Potato","Cauliflower","Tomato","Cumin","Turmeric","Whole Wheat Flour","Oil"]},
        {"name":"Egg Curry + Rice","kcal":278,"protein":18.4,"carbs":28.6,"fat":10.6,"fiber":1.4,"diet":"non-vegetarian","gi":42,"healthy_score":8,"tags":["Pan India","High Protein"],"ingredients":["Boiled Eggs","Tomato","Onion","Coconut","Spices","Rice","Oil"]},
        {"name":"Avial + Rice","kcal":226,"protein":5.4,"carbs":31.6,"fat":7.8,"fiber":5.8,"diet":"vegetarian","gi":48,"healthy_score":9,"tags":["Kerala","High Fiber"],"ingredients":["Mixed Vegetables","Coconut","Curd","Curry Leaves","Coconut Oil","Rice","Green Chilli"]},
    ],
    "🍵 Snacks": [
        {"name":"Sprouts Chaat","kcal":88,"protein":6.8,"carbs":12.4,"fat":0.8,"fiber":3.6,"diet":"vegetarian","gi":22,"healthy_score":10,"tags":["High Protein","Low Cal","Diabetic Friendly"],"ingredients":["Sprouted Moong","Tomato","Cucumber","Lemon","Chaat Masala","Onion","Coriander"]},
        {"name":"Dhokla","kcal":148,"protein":7.2,"carbs":22.4,"fat":3.2,"fiber":1.6,"diet":"vegetarian","gi":35,"healthy_score":9,"tags":["Gujarat","Steamed","Probiotic"],"ingredients":["Besan","Yogurt","Eno","Mustard","Curry Leaves","Sesame","Sugar","Lemon"]},
        {"name":"Makhana (Roasted)","kcal":347,"protein":9.7,"carbs":76.9,"fat":0.1,"fiber":14.5,"diet":"vegetarian","gi":38,"healthy_score":10,"tags":["High Fiber","Low Fat","Antioxidant"],"ingredients":["Fox Nuts","Ghee","Salt","Cumin","Black Pepper"]},
        {"name":"Roasted Chana","kcal":364,"protein":22.4,"carbs":52.6,"fat":5.2,"fiber":12.8,"diet":"vegetarian","gi":28,"healthy_score":10,"tags":["High Protein","High Fiber","Budget"],"ingredients":["Dried Chickpeas","Salt","Spices"]},
        {"name":"Sattu Drink","kcal":88,"protein":5.8,"carbs":13.4,"fat":1.2,"fiber":2.8,"diet":"vegetarian","gi":22,"healthy_score":10,"tags":["Bihar","High Protein","Cooling"],"ingredients":["Roasted Gram Flour","Water","Lemon","Black Salt","Green Chilli"]},
        {"name":"Masala Chai","kcal":48,"protein":1.8,"carbs":6.4,"fat":1.8,"fiber":0.0,"diet":"vegetarian","gi":45,"healthy_score":7,"tags":["Pan India","Warming","Antioxidant"],"ingredients":["Tea","Milk","Sugar","Ginger","Cardamom","Cinnamon"]},
        {"name":"Lassi (Salted)","kcal":58,"protein":3.0,"carbs":5.8,"fat":2.4,"fiber":0.0,"diet":"vegetarian","gi":35,"healthy_score":8,"tags":["Punjab","Probiotic","Refreshing"],"ingredients":["Curd","Water","Salt","Roasted Cumin"]},
        {"name":"Khandvi","kcal":128,"protein":6.4,"carbs":16.8,"fat":3.8,"fiber":1.2,"diet":"vegetarian","gi":38,"healthy_score":9,"tags":["Gujarat","Low Cal","Protein Rich"],"ingredients":["Besan","Yogurt","Turmeric","Mustard","Coconut","Coriander","Sesame"]},
        {"name":"Pani Puri","kcal":178,"protein":4.2,"carbs":28.4,"fat":5.8,"fiber":2.4,"diet":"vegetarian","gi":52,"healthy_score":5,"tags":["Street Food","Tangy"],"ingredients":["Semolina","Potato","Chickpeas","Tamarind","Mint","Cumin","Black Salt"]},
        {"name":"Corn on the Cob","kcal":86,"protein":3.2,"carbs":18.4,"fat":1.2,"fiber":2.4,"diet":"vegetarian","gi":52,"healthy_score":8,"tags":["Seasonal","Antioxidant"],"ingredients":["Sweet Corn","Lemon","Chilli","Salt","Butter"]},
        {"name":"Bhel Puri","kcal":218,"protein":5.4,"carbs":36.2,"fat":6.8,"fiber":2.8,"diet":"vegetarian","gi":58,"healthy_score":5,"tags":["Mumbai","Street Food"],"ingredients":["Puffed Rice","Sev","Onion","Tomato","Tamarind Chutney","Coriander","Lemon"]},
        {"name":"Samosa (Baked)","kcal":178,"protein":4.8,"carbs":26.4,"fat":6.4,"fiber":2.8,"diet":"vegetarian","gi":55,"healthy_score":6,"tags":["North India","Tea Time"],"ingredients":["Whole Wheat Flour","Potato","Green Peas","Spices","Oil"]},
    ],
    "🌙 Dinner": [
        {"name":"Moong Dal + Chapati","kcal":248,"protein":12.4,"carbs":38.4,"fat":3.2,"fiber":5.8,"diet":"vegetarian","gi":30,"healthy_score":10,"tags":["Light","Easy Digest","Weight Loss"],"ingredients":["Yellow Moong Dal","Whole Wheat Flour","Turmeric","Ghee","Cumin","Salt"]},
        {"name":"Palak Soup + Roti","kcal":180,"protein":7.2,"carbs":28.8,"fat":3.6,"fiber":5.4,"diet":"vegetarian","gi":28,"healthy_score":10,"tags":["Iron Rich","Light","Healthy"],"ingredients":["Spinach","Onion","Garlic","Ginger","Cream","Whole Wheat Flour","Spices"]},
        {"name":"Masoor Dal + Brown Rice","kcal":206,"protein":10.8,"carbs":34.2,"fat":2.4,"fiber":6.8,"diet":"vegetarian","gi":32,"healthy_score":9,"tags":["High Fiber","Iron Rich"],"ingredients":["Red Lentils","Brown Rice","Onion","Tomato","Spices","Oil","Garlic"]},
        {"name":"Tandoori Chicken + Salad","kcal":198,"protein":26.4,"carbs":4.8,"fat":8.2,"fiber":1.6,"diet":"non-vegetarian","gi":20,"healthy_score":10,"tags":["High Protein","Low Carb","Grilled"],"ingredients":["Chicken","Yogurt","Tandoori Masala","Lemon","Mixed Salad","Oil"]},
        {"name":"Paneer Bhurji + Chapati","kcal":388,"protein":16.8,"carbs":34.6,"fat":18.8,"fiber":2.8,"diet":"vegetarian","gi":38,"healthy_score":7,"tags":["North India","High Protein"],"ingredients":["Paneer","Onion","Tomato","Green Chilli","Spices","Whole Wheat Flour","Oil"]},
        {"name":"Grilled Fish + Veg","kcal":188,"protein":22.4,"carbs":8.4,"fat":7.6,"fiber":2.8,"diet":"non-vegetarian","gi":22,"healthy_score":10,"tags":["Omega-3","High Protein","Low Carb"],"ingredients":["Fish Fillet","Lemon","Garlic","Spices","Mixed Vegetables","Olive Oil"]},
        {"name":"Curd Rice","kcal":128,"protein":3.8,"carbs":22.4,"fat":2.8,"fiber":0.6,"diet":"vegetarian","gi":65,"healthy_score":7,"tags":["Tamil Nadu","Cooling","Probiotic"],"ingredients":["Rice","Curd","Mustard","Curry Leaves","Ginger","Green Chilli","Salt"]},
        {"name":"Vegetable Khichdi","kcal":148,"protein":6.4,"carbs":24.8,"fat":2.8,"fiber":3.4,"diet":"vegetarian","gi":52,"healthy_score":9,"tags":["Comfort Food","Easy Digest"],"ingredients":["Rice","Moong Dal","Mixed Vegetables","Ghee","Turmeric","Cumin"]},
        {"name":"Sarson Ka Saag + Makki Roti","kcal":326,"protein":10.8,"carbs":46.2,"fat":10.4,"fiber":9.4,"diet":"vegetarian","gi":38,"healthy_score":9,"tags":["Punjab Winter","Iron Rich"],"ingredients":["Mustard Greens","Spinach","Makki Atta","Ghee","Ginger","Garlic","Onion"]},
        {"name":"Chicken Soup","kcal":92,"protein":12.4,"carbs":6.8,"fat":2.4,"fiber":1.2,"diet":"non-vegetarian","gi":25,"healthy_score":10,"tags":["Light","High Protein","Healing"],"ingredients":["Chicken","Vegetables","Ginger","Garlic","Black Pepper","Bay Leaf","Salt"]},
        {"name":"Rajma + Chapati","kcal":294,"protein":15.4,"carbs":42.8,"fat":3.8,"fiber":9.4,"diet":"vegetarian","gi":29,"healthy_score":9,"tags":["Punjab","High Protein","High Fiber"],"ingredients":["Kidney Beans","Tomato","Onion","Spices","Whole Wheat Flour","Oil","Garlic"]},
        {"name":"Baingan Bharta + Roti","kcal":246,"protein":5.8,"carbs":34.6,"fat":7.6,"fiber":7.2,"diet":"vegetarian","gi":28,"healthy_score":9,"tags":["North India","Low Cal","Smoky"],"ingredients":["Roasted Aubergine","Tomato","Onion","Garlic","Spices","Whole Wheat Flour","Oil"]},
    ],
}

INGREDIENT_CATEGORIES = {
    "Dairy & Eggs":       ["Milk","Curd","Paneer","Ghee","Cream","Butter","Yogurt","Eggs","Boiled Eggs","Chaas"],
    "Lentils & Legumes":  ["Toor Dal","Moong Dal","Masoor Dal","Chana Dal","Urad Dal","Kidney Beans","Chickpeas","Rajma","Black Lentils","Green Moong Dal","Yellow Moong Dal","Red Lentils"],
    "Grains & Flours":    ["Basmati Rice","Brown Rice","Rice","Whole Wheat Flour","Semolina","Besan","Ragi","Bajra","Jowar","Broken Wheat","Makki Atta","Flattened Rice","Sago","Fox Nuts","Roasted Gram Flour","Chickpea Flour","Finger Millet Flour"],
    "Vegetables":         ["Potato","Onion","Tomato","Spinach","Cauliflower","Peas","Mixed Vegetables","Cucumber","Sweet Corn","Roasted Aubergine","Mustard Greens","Fenugreek Leaves","Mixed Salad"],
    "Meat & Fish":        ["Chicken","Mutton","Fish","Fish Fillet","Prawns","Eggs","Boiled Eggs"],
    "Spices & Condiments":["Turmeric","Cumin","Mustard","Coriander","Red Chilli","Garam Masala","Cardamom","Cinnamon","Bay Leaf","Black Pepper","Curry Leaves","Tamarind","Sambar Powder","Ginger","Garlic","Green Chilli","Kasuri Methi","Chaat Masala","Black Salt","Bisi Bele Bath Powder","Chole Masala","Tandoori Masala","Whole Spices","Spices","Salt"],
    "Nuts & Seeds":       ["Cashew","Peanuts","Sesame","Almond","Pistachio","Pumpkin Seeds"],
    "Sweeteners":         ["Sugar","Jaggery","Honey"],
    "Oils & Fats":        ["Oil","Coconut Oil","Mustard Oil","Olive Oil","Butter","Ghee"],
    "Fresh Herbs":        ["Coriander","Mint","Curry Leaves","Fenugreek Leaves"],
    "Beverages":          ["Tea","Coffee","Coconut Milk","Milk","Water"],
    "Specialty/Other":    ["Eno","Baking Soda","Saffron","Kokum","Fox Nuts","Sago","Fried Onion","Lemon","Kochu"],
}

def get_ingredient_category(ingredient: str) -> str:
    for cat, items in INGREDIENT_CATEGORIES.items():
        for item in items:
            if item.lower() in ingredient.lower() or ingredient.lower() in item.lower():
                return cat
    return "Others"

# ══════════════════════════════════════════════════════════════════════════════
# EXERCISE PLANS  (built-in, no API needed)
# ══════════════════════════════════════════════════════════════════════════════
EXERCISE_PLANS = {
    "Lose Weight": {
        "overview": "Calorie-deficit cardio + light resistance. Target 45–60 min/day, 5 days/week.",
        "days": [
            {"day":"Monday",    "type":"Cardio",    "activity":"Brisk Walk or Jog",        "duration":"45 min", "intensity":"Moderate", "calories_burned":280, "tips":"Keep heart rate at 65-75% max. Use stairs when possible."},
            {"day":"Tuesday",   "type":"Strength",  "activity":"Bodyweight Circuit",        "duration":"40 min", "intensity":"Moderate", "calories_burned":220, "tips":"Squats, push-ups, lunges, plank. 3 rounds."},
            {"day":"Wednesday", "type":"Yoga",      "activity":"Surya Namaskar + Yoga",     "duration":"45 min", "intensity":"Low",      "calories_burned":160, "tips":"12 rounds Surya Namaskar. Great for metabolism."},
            {"day":"Thursday",  "type":"Cardio",    "activity":"Cycling or Swimming",       "duration":"45 min", "intensity":"Moderate", "calories_burned":300, "tips":"Steady pace, maintain conversation speed."},
            {"day":"Friday",    "type":"Strength",  "activity":"Resistance Training",       "duration":"40 min", "intensity":"Moderate", "calories_burned":240, "tips":"Dumbbell rows, shoulder press, deadlift, core."},
            {"day":"Saturday",  "type":"Active",    "activity":"Dance / Zumba / Sport",     "duration":"60 min", "intensity":"High",     "calories_burned":380, "tips":"Fun activity! Bollywood dance is excellent."},
            {"day":"Sunday",    "type":"Rest",      "activity":"Light Walk + Stretching",   "duration":"30 min", "intensity":"Low",      "calories_burned":100, "tips":"Recovery day. Gentle yoga or foam rolling."},
        ]
    },
    "Gain Muscle": {
        "overview": "Progressive overload strength training. 4 days lifting, 1 active recovery. Target 1g protein/lb bodyweight.",
        "days": [
            {"day":"Monday",    "type":"Strength",  "activity":"Push Day (Chest/Shoulder/Triceps)", "duration":"55 min", "intensity":"High",     "calories_burned":300, "tips":"Bench press, OHP, lateral raise, tricep dips. Progressive overload."},
            {"day":"Tuesday",   "type":"Strength",  "activity":"Pull Day (Back/Biceps)",            "duration":"55 min", "intensity":"High",     "calories_burned":280, "tips":"Pull-ups, barbell row, bicep curl. Focus on squeeze."},
            {"day":"Wednesday", "type":"Active",    "activity":"Light Yoga / Stretching",           "duration":"40 min", "intensity":"Low",      "calories_burned":140, "tips":"Mobility work. Prevents injury. Hip flexors + hamstrings."},
            {"day":"Thursday",  "type":"Strength",  "activity":"Leg Day (Quads/Glutes/Hamstrings)", "duration":"60 min", "intensity":"High",     "calories_burned":360, "tips":"Squats, leg press, Romanian deadlift, calf raise."},
            {"day":"Friday",    "type":"Strength",  "activity":"Full Body Compound",                "duration":"55 min", "intensity":"High",     "calories_burned":320, "tips":"Deadlift, squat, bench, rows. Heavy compound movements."},
            {"day":"Saturday",  "type":"Cardio",    "activity":"Light Run / HIIT (short)",          "duration":"30 min", "intensity":"Moderate", "calories_burned":200, "tips":"Don't overtrain. 20 min HIIT max for muscle gainers."},
            {"day":"Sunday",    "type":"Rest",      "activity":"Complete Rest + Nutrition Focus",    "duration":"—",      "intensity":"—",        "calories_burned":0,   "tips":"Muscles grow on rest days. Sleep 8hrs. Prioritise protein intake."},
        ]
    },
    "Maintain Weight": {
        "overview": "Balanced mix of cardio and strength. 3-4 days/week, 30-45 min each. Focus on consistency.",
        "days": [
            {"day":"Monday",    "type":"Strength",  "activity":"Full Body Weights",         "duration":"40 min", "intensity":"Moderate", "calories_burned":240, "tips":"Compound movements. Focus on form over weight."},
            {"day":"Tuesday",   "type":"Cardio",    "activity":"Brisk Walk / Light Jog",    "duration":"35 min", "intensity":"Low",      "calories_burned":190, "tips":"Enjoy the outdoors. Morning walks boost mood."},
            {"day":"Wednesday", "type":"Yoga",      "activity":"Yoga / Pilates",            "duration":"40 min", "intensity":"Low",      "calories_burned":150, "tips":"Great for posture and flexibility. Reduces stress cortisol."},
            {"day":"Thursday",  "type":"Cardio",    "activity":"Cycling / Swimming",        "duration":"40 min", "intensity":"Moderate", "calories_burned":270, "tips":"Low-impact option. Great for joints."},
            {"day":"Friday",    "type":"Strength",  "activity":"Upper Body Focus",          "duration":"40 min", "intensity":"Moderate", "calories_burned":220, "tips":"Back, chest, shoulders. Functional strength."},
            {"day":"Saturday",  "type":"Active",    "activity":"Sport / Outdoor Activity",  "duration":"60 min", "intensity":"Moderate", "calories_burned":300, "tips":"Cricket, badminton, football — fun counts as exercise!"},
            {"day":"Sunday",    "type":"Rest",      "activity":"Light Stretching / Walk",   "duration":"20 min", "intensity":"Low",      "calories_burned":80,  "tips":"Active rest. Don't stay completely sedentary."},
        ]
    },
    "Lose Weight (Fast)": {
        "overview": "Aggressive HIIT + strength circuit. High intensity 5-6 days. Combine with strict diet. Consult doctor if health conditions.",
        "days": [
            {"day":"Monday",    "type":"HIIT",      "activity":"HIIT Cardio",               "duration":"30 min", "intensity":"Very High", "calories_burned":380, "tips":"20s on, 10s off. Burpees, jump squats, high knees."},
            {"day":"Tuesday",   "type":"Strength",  "activity":"Circuit Training",          "duration":"45 min", "intensity":"High",      "calories_burned":340, "tips":"Minimal rest between sets. Keep heart rate elevated."},
            {"day":"Wednesday", "type":"Cardio",    "activity":"Run / Cycle",               "duration":"50 min", "intensity":"High",      "calories_burned":400, "tips":"Increase pace gradually. Target 80% max heart rate."},
            {"day":"Thursday",  "type":"HIIT",      "activity":"Tabata + Core",             "duration":"35 min", "intensity":"Very High", "calories_burned":360, "tips":"4 min Tabata rounds. Plank, mountain climbers, Russian twists."},
            {"day":"Friday",    "type":"Strength",  "activity":"Full Body Weights",         "duration":"45 min", "intensity":"High",      "calories_burned":310, "tips":"Compound lifts with short rest. Superset exercises."},
            {"day":"Saturday",  "type":"Cardio",    "activity":"Long Walk / Hike",          "duration":"75 min", "intensity":"Moderate",  "calories_burned":400, "tips":"Steady-state cardio for active recovery and fat burn."},
            {"day":"Sunday",    "type":"Rest",      "activity":"Yoga + Full Rest",          "duration":"30 min", "intensity":"Low",       "calories_burned":100, "tips":"Essential recovery. Overtraining backfires. Listen to body."},
        ]
    },
    "Gain Weight": {
        "overview": "Strength focus with minimal cardio. Eat calorie surplus. Prioritise compound lifts and sleep.",
        "days": [
            {"day":"Monday",    "type":"Strength",  "activity":"Lower Body Heavy",          "duration":"60 min", "intensity":"High",     "calories_burned":300, "tips":"Squats, deadlifts, leg press. These build most mass."},
            {"day":"Tuesday",   "type":"Strength",  "activity":"Upper Body Push",           "duration":"55 min", "intensity":"High",     "calories_burned":270, "tips":"Bench, OHP, dips. Eat a high-protein meal 2hrs before."},
            {"day":"Wednesday", "type":"Light",     "activity":"Light Walk + Flexibility",  "duration":"30 min", "intensity":"Low",      "calories_burned":100, "tips":"Don't overtrain. Active recovery only."},
            {"day":"Thursday",  "type":"Strength",  "activity":"Upper Body Pull",           "duration":"55 min", "intensity":"High",     "calories_burned":260, "tips":"Rows, pull-ups, face pulls. Build that thick back."},
            {"day":"Friday",    "type":"Strength",  "activity":"Full Body Power",           "duration":"60 min", "intensity":"High",     "calories_burned":320, "tips":"Heavy compound: deadlift, squat, bench. Progressive overload is key."},
            {"day":"Saturday",  "type":"Light",     "activity":"Walk / Gentle Yoga",        "duration":"30 min", "intensity":"Low",      "calories_burned":90,  "tips":"Minimal calorie burn — focus on eating well today."},
            {"day":"Sunday",    "type":"Rest",      "activity":"Rest + Meal Prep",          "duration":"—",      "intensity":"—",        "calories_burned":0,   "tips":"Meal prep for the week. Sleep is when you grow."},
        ]
    },
}

TYPE_COLORS = {
    "HIIT": "#FF4B6E", "Strength": "#FF6B2B", "Cardio": "#00D4FF",
    "Yoga": "#4ECBA0", "Active": "#F5A623", "Light": "#4ECBA0",
    "Rest": "rgba(255,248,240,.3)"
}

# ══════════════════════════════════════════════════════════════════════════════
# NUTRITION CALC
# ══════════════════════════════════════════════════════════════════════════════
def calc_bmr(gender, weight, height, age):
    b = 10 * weight + 6.25 * height - 5 * age
    return b + 5 if gender == "Male" else b - 161

def calc_targets(profile):
    bmr   = calc_bmr(profile["gender"], profile["weight"], profile["height"], profile["age"])
    tdee  = bmr * ACTIVITY_FACTORS.get(profile["activity"], 1.375)
    kcal  = max(1200, round(tdee + GOAL_DELTA.get(profile["goal"], 0)))
    sp    = GOAL_SPLITS.get(profile["goal"], (0.25, 0.50, 0.25))
    bmi   = profile["weight"] / (profile["height"] / 100) ** 2
    cats  = [(0,18.5,"Underweight","#00D4FF"),(18.5,25,"Healthy Weight","#4ECBA0"),(25,30,"Overweight","#F5A623"),(30,35,"Obese I","#FF6B2B"),(35,100,"Obese II+","#FF4B6E")]
    bmi_cat, bmi_col = next(((c, col) for lo,hi,c,col in cats if lo <= bmi < hi), ("—","#888"))
    ws = max(40, min(100, (85 if 18.5<=bmi<=24.9 else 65) + (3 if profile["diet"]=="Vegetarian" else 0)))
    return {
        "bmr": round(bmr), "tdee": round(tdee), "kcal": kcal,
        "prot": round(kcal*sp[0]/4, 1), "carbs": round(kcal*sp[1]/4, 1), "fat": round(kcal*sp[2]/9, 1),
        "bmi": round(bmi, 1), "bmi_cat": bmi_cat, "bmi_col": bmi_col,
        "water": round(profile["weight"]*35 + 200), "wellness": ws,
    }

def get_medical_rules(conditions):
    rules = {}
    for c in conditions:
        if "Diabetes" in c:     rules["max_gi"] = 55
        if "Hypertension" in c: rules["low_sodium"] = True
        if "Anaemia" in c:      rules["high_iron"] = True
        if "PCOS" in c:         rules["max_gi"] = 50
    return rules

def get_recommended_dishes(profile, targets, meal_type, n=4):
    all_dishes = CURATED_MENU.get(meal_type, [])
    rules = profile.get("medical_rules", {})
    scored = []
    for d in all_dishes:
        if profile["diet"] == "Vegetarian" and d["diet"] == "non-vegetarian":
            continue
        if rules.get("max_gi") and d.get("gi") and d["gi"] > rules["max_gi"]:
            continue
        score = d.get("healthy_score", 5)
        goal  = profile.get("goal", "")
        if "Lose" in goal and d["kcal"] < 200:   score += 2
        if "Lose" in goal and d.get("fiber",0)>3: score += 1
        if "Gain Muscle" in goal and d["protein"]>8: score += 2
        if "Gain" in goal and d["kcal"] > 250:    score += 1
        if d["protein"] > 10:                     score += 1
        if "Anaemia" in profile.get("medical",[]) and any("Spinach" in i or "Dal" in i for i in d.get("ingredients",[])): score += 2
        scored.append((score, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:n]]

# ══════════════════════════════════════════════════════════════════════════════
# AI HEALTH ADVISOR  (rule-based intelligence, no API key needed)
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_health_plan(profile, targets, today_log):
    """Generate personalised AI health advice based on profile and current log."""
    bmi  = targets["bmi"]
    goal = profile["goal"]
    diet = profile["diet"]
    conds = profile.get("medical", [])
    age  = profile["age"]
    gender = profile["gender"]
    region = profile.get("region", "North")

    logged_kcal = sum(float(d.get("kcal",0) or 0) for mt in today_log.values() for d in mt)
    logged_prot = sum(float(d.get("protein",0) or 0) for mt in today_log.values() for d in mt)

    sections = {}

    # ── 1. BMI Assessment ──────────────────────────────────────────
    if bmi < 18.5:
        bmi_msg = f"Your BMI of {bmi} indicates **underweight**. Focus on calorie-dense nutritious foods. Avoid ultra-processed foods even while increasing calories."
        bmi_foods = "Nuts, ghee, full-fat dairy, avocado, banana, paneer, rajma, eggs, ragi ladoo, groundnut chikki."
    elif bmi <= 24.9:
        bmi_msg = f"Your BMI of {bmi} is in the **healthy range**. Maintain current habits. Focus on food quality over quantity."
        bmi_foods = "Continue with balanced dal-roti-sabzi. Seasonal fruits. Varied protein sources."
    elif bmi <= 29.9:
        bmi_msg = f"Your BMI of {bmi} indicates **overweight**. Aim to reduce 0.5kg/week through diet and exercise. Avoid crash dieting."
        bmi_foods = "Prioritise: moong dal, green vegetables, sprouts, besan chilla, ragi. Reduce: white rice, maida, fried snacks, sugar."
    else:
        bmi_msg = f"Your BMI of {bmi} indicates **obesity**. Medical supervision is advised alongside lifestyle changes. Start gentle exercise."
        bmi_foods = "Begin with: 1200-1400 kcal structured diet. Khichdi, salads, dal soups, grilled proteins. Avoid: sugar, fried foods, packaged snacks completely."
    sections["bmi"] = {"title":"BMI & Weight Assessment","content":bmi_msg,"detail":f"**Best foods for you:** {bmi_foods}"}

    # ── 2. Daily Diet Plan ─────────────────────────────────────────
    diet_plan = []
    if goal == "Lose Weight" or goal == "Lose Weight (Fast)":
        diet_plan = [
            ("🌅 Breakfast (7-8am)", f"Besan chilla (2 pcs) + green chutney + 1 fruit | OR | Moong dal chilla + curd | ~{int(targets['kcal']*0.22)} kcal"),
            ("🍎 Mid-morning (10am)", "1 fruit (papaya/guava/watermelon) + sattu drink or lassi | ~150 kcal"),
            ("☀️ Lunch (1pm)",        f"1 bowl dal + 2 chapati + 1 bowl sabzi + small salad | ~{int(targets['kcal']*0.32)} kcal"),
            ("🍵 Evening (4pm)",      "Sprouts chaat OR roasted chana OR makhana | ~100 kcal"),
            ("🌙 Dinner (7-8pm)",     f"1 bowl moong dal soup + 1-2 chapati + grilled/steamed vegetable | ~{int(targets['kcal']*0.24)} kcal"),
        ]
    elif goal == "Gain Muscle":
        diet_plan = [
            ("🌅 Breakfast (7am)",    f"4 egg whites + 2 whole eggs + 2 whole wheat toast + banana | OR | Paneer bhurji + 3 roti + milk | ~{int(targets['kcal']*0.25)} kcal"),
            ("Pre-workout (10am)",    "Banana + sattu drink OR peanut butter toast | ~250 kcal"),
            ("☀️ Lunch (1pm)",        f"Chicken/paneer curry + brown rice + dal + salad | ~{int(targets['kcal']*0.32)} kcal"),
            ("Post-workout (4pm)",    "Whey protein OR paneer + fruits + nuts | ~300 kcal"),
            ("🌙 Dinner (7-8pm)",     f"Grilled fish/chicken OR rajma/chole + roti + vegetables + curd | ~{int(targets['kcal']*0.28)} kcal"),
        ]
    elif goal == "Gain Weight":
        diet_plan = [
            ("🌅 Breakfast (7am)",    "Full Indian breakfast: paratha + curd + pickle + lassi | ~500 kcal"),
            ("Mid-morning (10am)",    "Banana milkshake + handful nuts + groundnut chikki | ~350 kcal"),
            ("☀️ Lunch (1pm)",        "2 bowls rice + 2 curries + dal + raita + papad | ~700 kcal"),
            ("🍵 Evening (4pm)",      "Samosa + chai OR banana shake OR thick curd | ~300 kcal"),
            ("🌙 Dinner (7-8pm)",     "Roti + sabzi + paneer/dal + kheer or halwa | ~600 kcal"),
        ]
    else:  # Maintain
        diet_plan = [
            ("🌅 Breakfast (7-8am)", f"Idli-sambar OR dalia OR poha + fruit + chai | ~{int(targets['kcal']*0.22)} kcal"),
            ("Mid-morning (10am)",   "Fruit + handful nuts | ~150 kcal"),
            ("☀️ Lunch (1pm)",       f"Dal + roti + sabzi + salad + curd | ~{int(targets['kcal']*0.35)} kcal"),
            ("🍵 Evening (4pm)",     "Chai + light snack (dhokla, sprouts, roasted chana) | ~150 kcal"),
            ("🌙 Dinner (7-8pm)",   f"Light dal/soup + 2 roti + vegetable | ~{int(targets['kcal']*0.25)} kcal"),
        ]
    sections["diet"] = {"title":"Your Daily Diet Plan", "plan": diet_plan}

    # ── 3. Medical Condition Advice ────────────────────────────────
    cond_advice = []
    for c in conds:
        if c == "Diabetes":
            cond_advice.append(("🩸","Diabetes Management","Choose low-GI foods: bajra roti, brown rice, moong dal, leafy vegetables. Eat every 3 hours — small meals. Never skip breakfast. Avoid: white rice, maida, sugar, fruit juices. Include: karela, methi, amla, cinnamon tea. Monitor blood sugar 2hrs after meals."))
        if c == "Hypertension":
            cond_advice.append(("❤️","Hypertension (BP) Management","Limit sodium strictly: no pickles, papads, packaged food, extra salt. DASH diet: increase potassium (banana, coconut water, spinach), magnesium (nuts, seeds), calcium (curd, ragi). Avoid: red meat, full-fat dairy, caffeine excess, alcohol. Include: garlic, flaxseeds, watermelon, oatmeal."))
        if c == "Anaemia":
            cond_advice.append(("🩸","Anaemia (Iron Deficiency)","Iron-rich Indian foods: palak dal, rajma, horse gram, til, dried dates, ragi, moringa. Always pair with Vitamin C (amla, lemon, guava) for 3× better absorption. Avoid: tea, coffee, calcium supplements within 1hr of iron-rich meals. Cook in iron kadhai — it adds dietary iron."))
        if c == "PCOS":
            cond_advice.append(("🌸","PCOS Management","Anti-inflammatory, low-GI diet is key. Include: methi seeds (soak overnight, eat morning), flaxseeds, turmeric milk, omega-3 (fish/walnuts). Avoid: sugar, refined carbs, dairy excess, soy in large amounts. Exercise: yoga + 30 min cardio daily reduces androgen levels. Intermittent fasting (16:8) can help."))
        if c == "Thyroid":
            cond_advice.append(("🦋","Thyroid Management","Hypothyroid: increase iodine (iodised salt, seafood). Selenium: brazil nuts, sunflower seeds. Cook cruciferous vegetables — don't eat raw (cauliflower, cabbage, radish reduce T4). Hyperthyroid: reduce iodine, avoid seaweed. Both: take medication 30-60 min before food. Exercise: yoga is beneficial."))
    sections["medical"] = {"title":"Medical Condition Guidance", "items": cond_advice}

    # ── 4. Micronutrient Gaps ─────────────────────────────────────
    gaps = []
    if diet == "Vegetarian":
        gaps.append(("B12","🧠","Critical for vegetarians","Take B12 supplement (500mcg/day cyanocobalamin). Include fortified milk/curd. Fermented foods (idli batter, kanji) have trace B12 from bacteria — not enough alone."))
    if age >= 35 or gender == "Female":
        gaps.append(("Calcium","🦷","Important for your age/gender","Ragi is top plant calcium source (364mg/100g). Curd daily. Sesame seeds in chutney. Moringa leaves. Avoid excess tea — it blocks calcium absorption."))
    if region in ["North","Central"] or diet == "Vegetarian":
        gaps.append(("Vitamin D","☀️","Common Indian deficiency","Get 15-20 min of morning sunlight (before 10am) on arms daily. Most Indians are deficient. Supplement 1000-2000 IU/day Vitamin D3 + K2 is often recommended."))
    gaps.append(("Omega-3","🐟","Often missed in Indian diets","Include: walnuts, flaxseeds (alsi), chia seeds, mustard oil. Non-veg: sardines, mackerel, rohu fish 2-3x/week. Omega-3 reduces inflammation, improves heart health and mood."))
    sections["nutrients"] = {"title":"Micronutrient Watch List", "items": gaps}

    # ── 5. Today's Gap Analysis ────────────────────────────────────
    kcal_gap = targets["kcal"] - logged_kcal
    prot_gap = targets["prot"] - logged_prot
    gaps_today = []
    if logged_kcal == 0:
        gaps_today.append("No meals logged today. Start by logging your breakfast in the Meal Logger tab.")
    else:
        if kcal_gap > 300:
            gaps_today.append(f"You still need {kcal_gap:.0f} more kcal today. Add a protein-rich meal or snack.")
        elif kcal_gap < -200:
            gaps_today.append(f"You've exceeded your target by {abs(kcal_gap):.0f} kcal. Skip evening snacks and have light dinner.")
        else:
            gaps_today.append("Calorie intake is well-balanced today. Great discipline!")
        if prot_gap > 20:
            gaps_today.append(f"Protein is short by {prot_gap:.0f}g. Add: paneer sabzi, dal, 2 eggs, or Greek yogurt.")
        elif prot_gap < 5:
            gaps_today.append("Protein target nearly met — excellent!")
    sections["today"] = {"title":"Today's Gap Analysis", "items": gaps_today}

    return sections

# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE API INTEGRATION (Optional — if anthropic package installed + key set)
# ══════════════════════════════════════════════════════════════════════════════
def call_claude_api(prompt: str, api_key: str) -> str:
    """Call Claude claude-sonnet-4-20250514 for AI health advice."""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            messages=[{"role":"user","content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Could not reach Claude API: {str(e)}"

def build_claude_prompt(profile, targets, question: str) -> str:
    conds = ", ".join(profile.get("medical",[])) or "None"
    return f"""You are Nourish, an expert Indian nutritionist and health coach. 
Answer specifically for this user. Be practical, India-specific, reference Indian foods.

USER PROFILE:
- Name: {profile['name']}, {profile['gender']}, Age {profile['age']}
- Weight: {profile['weight']}kg, Height: {profile['height']}cm, BMI: {targets['bmi']} ({targets['bmi_cat']})
- Goal: {profile['goal']}, Diet: {profile['diet']}, Region: {profile.get('region','North')} India
- Activity: {profile['activity']}
- Health conditions: {conds}
- Daily calorie target: {targets['kcal']} kcal | Protein: {targets['prot']}g | Carbs: {targets['carbs']}g | Fat: {targets['fat']}g
- Water target: {targets['water']}ml/day

USER QUESTION: {question}

Provide a clear, actionable, India-specific answer. Use bullet points. Reference specific Indian dishes, ingredients, and practices. Keep response under 400 words."""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
today      = datetime.date.today()
today_str  = today.isoformat()
for k,v in [("meal_log",{}),("weekly_plan",{}),("shopping_list",{}),("water_glasses",0),("ai_chat",[])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="logo">🥗 Nourish</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:.25em;color:rgba(255,248,240,.3);text-transform:uppercase;margin-bottom:20px">Indian Diet Planner v4</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**👤 Profile**")
    name   = st.text_input("Name", value=st.session_state.get("name",""), placeholder="Your name", key="sb_name")
    gender = st.selectbox("Gender", ["Female","Male"], key="sb_gender")
    age    = st.slider("Age", 16, 80, 28, key="sb_age")
    weight = st.slider("Weight (kg)", 35, 150, 65, key="sb_weight")
    height = st.slider("Height (cm)", 140, 210, 162, key="sb_height")
    st.divider()

    st.markdown("**🎯 Goals**")
    activity = st.selectbox("Activity Level", list(ACTIVITY_FACTORS.keys()), index=2, key="sb_activity")
    goal     = st.selectbox("Goal", list(GOAL_DELTA.keys()), index=2, key="sb_goal")
    diet     = st.selectbox("Diet", ["Vegetarian","Non-Vegetarian"], key="sb_diet")
    region   = st.selectbox("Region", list(REGIONAL_STATES.keys()), key="sb_region")
    st.divider()

    st.markdown("**🏥 Health Conditions**")
    conditions = st.multiselect("Select if applicable", ["Diabetes","Hypertension","Anaemia","PCOS","Thyroid"], key="sb_conds", placeholder="None")
    st.divider()

    st.markdown("**💧 Water Tracker**")
    wg = st.session_state["water_glasses"]
    wc1, wc2, wc3 = st.columns([1,2,1])
    with wc1:
        if st.button("−", key="w_m"): st.session_state["water_glasses"] = max(0, wg-1)
    with wc2:
        st.markdown(f'<div style="text-align:center;font-family:Playfair Display,serif;font-size:22px;font-weight:700;color:#00D4FF">{wg} 🥛</div>', unsafe_allow_html=True)
    with wc3:
        if st.button("+", key="w_p"): st.session_state["water_glasses"] = wg + 1

    if name: st.session_state["name"] = name

profile = {
    "name": name or "Friend", "gender": gender, "age": age, "weight": weight,
    "height": height, "activity": activity, "goal": goal, "diet": diet,
    "region": region, "medical": conditions, "medical_rules": get_medical_rules(conditions),
}
targets = calc_targets(profile)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
    "🏠 Dashboard",
    "📝 Meal Logger",
    "🍽️ Curated Menu",
    "⭐ Recommendations",
    "📅 Weekly Planner",
    "🛒 Shopping List",
    "🤖 AI Health Advisor",
    "🔬 Nutrients",
    "📊 Progress",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    greet = profile["name"] if profile["name"] != "Friend" else ""
    st.markdown(
        f'<div class="eyebrow">Dashboard</div>'
        f'<div class="h1">Namaste{(" "+greet) if greet else ""} 🙏</div>'
        f'<div style="color:var(--muted);font-family:Space Mono,monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;margin:6px 0 24px">'
        f'Your personalised Indian wellness plan</div>',
        unsafe_allow_html=True
    )
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("🔥 Daily Calories", f"{targets['kcal']:,}", f"BMR {targets['bmr']:,}")
    k2.metric("⚖️ BMI", targets["bmi"], targets["bmi_cat"])
    k3.metric("💪 Protein", f"{targets['prot']}g", "daily target")
    k4.metric("💧 Water", f"{targets['water']:,}ml", f"{st.session_state['water_glasses']} glasses")
    k5.metric("⭐ Wellness", targets["wellness"], "out of 100")
    st.divider()

    today_log = st.session_state["meal_log"].get(today_str, {})
    logged_dishes = [d for mt in today_log.values() for d in mt]
    total_kcal  = sum(float(d.get("kcal",0) or 0) for d in logged_dishes)
    total_prot  = sum(float(d.get("protein",0) or 0) for d in logged_dishes)
    total_carbs = sum(float(d.get("carbs",0) or 0) for d in logged_dishes)
    total_fat   = sum(float(d.get("fat",0) or 0) for d in logged_dishes)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="eyebrow">Nutrition Mandala</div>', unsafe_allow_html=True)
        def ring_offset(got, target, circ):
            pct = min(1.0, got/target) if target > 0 else 0
            return circ * (1 - pct)
        p_off = ring_offset(total_prot,  targets["prot"],  565)
        c_off = ring_offset(total_carbs, targets["carbs"], 408)
        f_off = ring_offset(total_fat,   targets["fat"],   251)
        ov    = round(min(100, total_kcal / targets["kcal"] * 100)) if targets["kcal"] else 0
        st.markdown(f"""
        <div style="display:flex;justify-content:center;margin:12px 0">
        <svg viewBox="0 0 220 220" width="230">
          <circle cx="110" cy="110" r="90" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
          <circle cx="110" cy="110" r="65" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
          <circle cx="110" cy="110" r="40" fill="none" stroke="rgba(255,248,240,0.05)" stroke-width="22"/>
          <circle cx="110" cy="110" r="90" fill="none" stroke="#FF6B2B" stroke-width="22" stroke-linecap="round" stroke-dasharray="565" stroke-dashoffset="{p_off:.0f}" transform="rotate(-90 110 110)"/>
          <circle cx="110" cy="110" r="65" fill="none" stroke="#F5A623" stroke-width="22" stroke-linecap="round" stroke-dasharray="408" stroke-dashoffset="{c_off:.0f}" transform="rotate(-90 110 110)"/>
          <circle cx="110" cy="110" r="40" fill="none" stroke="#4ECBA0" stroke-width="22" stroke-linecap="round" stroke-dasharray="251" stroke-dashoffset="{f_off:.0f}" transform="rotate(-90 110 110)"/>
          <text x="110" y="104" text-anchor="middle" font-family="Playfair Display,serif" font-size="28" font-weight="700" fill="#FF6B2B">{ov}%</text>
          <text x="110" y="122" text-anchor="middle" font-family="Space Mono,monospace" font-size="9" fill="rgba(255,248,240,0.5)" letter-spacing="2">DAILY GOAL</text>
        </svg></div>
        <div style="display:flex;gap:20px;justify-content:center;margin-bottom:12px;flex-wrap:wrap">
          <span style="font-size:12px;color:var(--muted)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#FF6B2B;margin-right:6px"></span>Protein (outer)</span>
          <span style="font-size:12px;color:var(--muted)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#F5A623;margin-right:6px"></span>Carbs (mid)</span>
          <span style="font-size:12px;color:var(--muted)"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#4ECBA0;margin-right:6px"></span>Fat (inner)</span>
        </div>
        """, unsafe_allow_html=True)
        for label, got, target, unit in [("🔥 Calories", total_kcal, targets["kcal"], "kcal"), ("💪 Protein", total_prot, targets["prot"],"g"), ("⚡ Carbs", total_carbs, targets["carbs"],"g"), ("🫒 Fat", total_fat, targets["fat"],"g")]:
            pct = min(100, int(got/target*100)) if target > 0 else 0
            st.markdown(f"**{label}** — {round(got)} / {round(target)} {unit}")
            st.progress(pct/100)

    with col_r:
        st.markdown('<div class="eyebrow">Today\'s Meals</div>', unsafe_allow_html=True)
        if logged_dishes:
            for mt_key, dishes in today_log.items():
                if not dishes: continue
                st.markdown(f"**{mt_key}**")
                for d in dishes:
                    kv = float(d.get("kcal",0) or 0)
                    pv = float(d.get("protein",0) or 0)
                    st.markdown(
                        f'<div class="lr"><span style="font-size:13px;font-weight:600">{d["name"]}</span>'
                        f'<div style="display:flex;gap:5px;flex-wrap:wrap">'
                        f'{mp("k",f"{kv:.0f} kcal")}{mp("p",f"P {pv:.0f}g")}</div></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                '<div style="background:rgba(255,107,43,.05);border:1.5px dashed rgba(255,107,43,.2);'
                'border-radius:12px;padding:32px;text-align:center;color:var(--muted)">'
                '<div style="font-size:32px;margin-bottom:8px">🍽️</div>'
                '<div>No meals logged today yet</div>'
                '<div style="font-size:12px;margin-top:6px">Use <strong>Meal Logger</strong> or <strong>Curated Menu</strong></div></div>',
                unsafe_allow_html=True
            )
        st.divider()
        st.markdown('<div class="eyebrow">Smart Insights</div>', unsafe_allow_html=True)
        if total_kcal > 0 and total_kcal < targets["kcal"] * 0.5:
            st.markdown(alert("warn","⚠️ Less than 50% of calorie target consumed. Don't skip meals!"), unsafe_allow_html=True)
        elif total_kcal > targets["kcal"] * 1.1:
            st.markdown(alert("danger",f"🔴 Exceeded daily target by {total_kcal-targets['kcal']:.0f} kcal."), unsafe_allow_html=True)
        else:
            st.markdown(alert("good","✅ Calorie intake is on track today."), unsafe_allow_html=True)
        if total_prot < targets["prot"] * 0.6:
            st.markdown(alert("warn","💪 Protein is low — add dal, paneer, eggs or legumes."), unsafe_allow_html=True)
        wgt = round(targets["water"]/250)
        wgn = st.session_state["water_glasses"]
        if wgn < wgt // 2:
            st.markdown(alert("info",f"💧 Drink more water! Target: {wgt} glasses. Current: {wgn}."), unsafe_allow_html=True)
        else:
            st.markdown(alert("good",f"💧 Good hydration! {wgn}/{wgt} glasses today."), unsafe_allow_html=True)
        if diet == "Vegetarian":
            st.markdown(alert("info","🌱 Vegetarians: actively seek B12, Calcium & Zinc sources daily."), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MEAL LOGGER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div class="eyebrow">Daily Tracker</div>'
        '<div class="h1">Meal Logger 📝</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">Record every meal. Tracks calories, protein, carbs, fat & fibre in real time.</p>',
        unsafe_allow_html=True
    )
    log_date     = st.date_input("Date", value=datetime.date.today(), key="log_date_picker")
    log_date_str = log_date.isoformat()
    if log_date_str not in st.session_state["meal_log"]:
        st.session_state["meal_log"][log_date_str] = {}

    lc1, lc2 = st.columns(2)
    with lc1:
        st.markdown("#### ➕ Add a Meal")
        sel_mt = st.selectbox("Meal Time", list(CURATED_MENU.keys()), key="log_mt_sel")
        all_opts = {d["name"]: d for d in CURATED_MENU[sel_mt]}
        if diet == "Vegetarian":
            all_opts = {k:v for k,v in all_opts.items() if v["diet"]=="vegetarian"}
        dish_choice  = st.selectbox("Select Dish", ["-- Select --"] + list(all_opts.keys()), key="log_dish_sel")
        custom_name  = st.text_input("Or type custom dish", key="log_custom", placeholder="e.g. Homemade vegetable soup")
        serving_mult = st.slider("Serving size (1.0 = standard portion)", 0.5, 3.0, 1.0, 0.25, key="log_serving")

        if dish_choice != "-- Select --":
            d_prev = all_opts[dish_choice]
            prev_kcal  = str(round(d_prev["kcal"] * serving_mult)) + " kcal"
            prev_prot  = "P " + f"{d_prev['protein'] * serving_mult:.0f}" + "g"
            prev_carbs = "C " + f"{d_prev['carbs'] * serving_mult:.0f}" + "g"
            prev_fat   = "F " + f"{d_prev.get('fat', 0) * serving_mult:.0f}" + "g"
            prev_name  = d_prev["name"]
            prev_html  = (
                '<div class="card" style="margin-top:8px">'
                '<div style="font-size:12px;font-weight:700;margin-bottom:6px">'
                + prev_name + " preview (×" + f"{serving_mult:.2f}" + ")</div>"
                + mp("k", prev_kcal) + mp("p", prev_prot)
                + mp("c", prev_carbs) + mp("f", prev_fat)
                + "</div>"
            )
            st.markdown(prev_html, unsafe_allow_html=True)

        if st.button("✅ Log This Meal", key="log_add_btn"):
            if dish_choice != "-- Select --":
                dish = dict(all_opts[dish_choice])
                dish["kcal"]      = round(dish["kcal"] * serving_mult)
                dish["protein"]   = round(dish["protein"] * serving_mult, 1)
                dish["carbs"]     = round(dish["carbs"] * serving_mult, 1)
                dish["fat"]       = round(dish.get("fat",0) * serving_mult, 1)
                dish["fiber"]     = round(dish.get("fiber",0) * serving_mult, 1)
                dish["serving"]   = serving_mult
                dish["logged_at"] = datetime.datetime.now().strftime("%H:%M")
                st.session_state["meal_log"][log_date_str].setdefault(sel_mt,[]).append(dish)
                st.success(f"✅ {dish['name']} logged!")
                st.rerun()
            elif custom_name.strip():
                cd = {"name":custom_name.strip(),"kcal":0,"protein":0,"carbs":0,"fat":0,"fiber":0,"serving":serving_mult,"logged_at":datetime.datetime.now().strftime("%H:%M"),"tags":["Custom"]}
                st.session_state["meal_log"][log_date_str].setdefault(sel_mt,[]).append(cd)
                st.success(f"✅ {custom_name} logged!")
                st.rerun()

        st.divider()
        st.markdown("**⚡ Quick Add Popular Dishes**")
        popular = [
            ("Idli + Sambar","🌅 Breakfast"),("Dal Tadka + Roti","☀️ Lunch"),
            ("Moong Dal + Chapati","🌙 Dinner"),("Sprouts Chaat","🍵 Snacks"),
            ("Besan Chilla","🌅 Breakfast"),("Rajma Chawal","☀️ Lunch"),
        ]
        qc = st.columns(2)
        for i, (dn, mt_quick) in enumerate(popular):
            with qc[i%2]:
                if st.button(f"+ {dn}", key=f"qa_{i}"):
                    found = next((d for d in CURATED_MENU.get(mt_quick,[]) if d["name"]==dn), None)
                    if found:
                        d2 = dict(found)
                        d2["serving"] = 1.0
                        d2["logged_at"] = datetime.datetime.now().strftime("%H:%M")
                        st.session_state["meal_log"][log_date_str].setdefault(mt_quick,[]).append(d2)
                        st.success(f"✅ {dn} added!")
                        st.rerun()

    with lc2:
        st.markdown(f"#### 📋 Log for {log_date.strftime('%A, %d %B %Y')}")
        day_log = st.session_state["meal_log"].get(log_date_str, {})
        dtk = dtp = dtca = dtf = dtfb = 0.0
        has_any = any(v for v in day_log.values())
        if not has_any:
            st.markdown(
                '<div style="background:rgba(255,248,240,.03);border:1.5px dashed rgba(255,248,240,.1);'
                'border-radius:12px;padding:40px;text-align:center;color:var(--muted)">'
                '<div style="font-size:32px">🥢</div>'
                '<div style="margin-top:8px">No meals logged for this day</div></div>',
                unsafe_allow_html=True
            )
        for mt_key, dishes in day_log.items():
            if not dishes: continue
            st.markdown(f"**{mt_key}**")
            for idx, d in enumerate(dishes):
                kv  = float(d.get("kcal",0) or 0);    pv  = float(d.get("protein",0) or 0)
                cv  = float(d.get("carbs",0) or 0);    fv  = float(d.get("fat",0) or 0)
                fb  = float(d.get("fiber",0) or 0)
                dtk += kv; dtp += pv; dtca += cv; dtf += fv; dtfb += fb
                c_d, c_x = st.columns([6,1])
                with c_d:
                    st.markdown(
                        f'<div class="lr">'
                        f'<div><div style="font-size:13px;font-weight:600">{d["name"]}</div>'
                        f'<div style="font-size:10px;color:var(--muted);margin-top:2px">{d.get("logged_at","")} · ×{d.get("serving",1.0):.1f}</div></div>'
                        f'<div style="display:flex;gap:5px;flex-wrap:wrap">'
                        f'{mp("k",f"{kv:.0f} kcal")}{mp("p",f"P{pv:.0f}g")}{mp("c",f"C{cv:.0f}g")}{mp("f",f"F{fv:.0f}g")}'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
                with c_x:
                    if st.button("🗑", key=f"del_{log_date_str}_{mt_key}_{idx}"):
                        st.session_state["meal_log"][log_date_str][mt_key].pop(idx)
                        st.rerun()

        st.divider()
        st.markdown("**📊 Day Summary**")
        s1,s2,s3,s4,s5 = st.columns(5)
        s1.metric("Calories", f"{dtk:.0f}", f"/{targets['kcal']}")
        s2.metric("Protein",  f"{dtp:.0f}g",  f"/{targets['prot']}g")
        s3.metric("Carbs",    f"{dtca:.0f}g", f"/{targets['carbs']}g")
        s4.metric("Fat",      f"{dtf:.0f}g",  f"/{targets['fat']}g")
        s5.metric("Fibre",    f"{dtfb:.0f}g", "/30g RDA")
        if dtk > 0:
            sc = 100
            sc -= min(30, int(abs(dtk - targets["kcal"]) / targets["kcal"] * 60))
            if dtp < targets["prot"] * 0.7: sc -= 15
            if dtfb < 15: sc -= 10
            sc = max(0, min(100, sc))
            hc = "#4ECBA0" if sc >= 70 else "#F5A623" if sc >= 50 else "#FF4B6E"
            st.markdown(
                f'<div style="background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:12px;padding:16px;text-align:center;margin-top:12px">'
                f'<div class="eyebrow" style="margin-bottom:4px">Day Health Score</div>'
                f'<div class="health-score" style="color:{hc}">{sc}</div>'
                f'<div style="font-size:12px;color:var(--muted);margin-top:4px">out of 100</div></div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CURATED MENU  (BUG FIX: no nested quotes in f-strings)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        '<div class="eyebrow">Traditional Indian Cuisine</div>'
        '<div class="h1">Curated Menu 🍽️</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">55 handpicked dishes favoured by 90% of Indian households — authentic nutrition data.</p>',
        unsafe_allow_html=True
    )
    mf1,mf2,mf3,mf4 = st.columns([2,1,1,1])
    menu_search = mf1.text_input("Search dishes or ingredients", placeholder="dal, biryani, paratha…", key="menu_search")
    menu_diet   = mf2.selectbox("Diet", ["All","Vegetarian","Non-Vegetarian"], key="menu_diet_filter")
    menu_health = mf3.selectbox("Health Filter", ["All","High Protein","Low GI","High Fiber","Low Calorie","Diabetic Friendly"], key="menu_health_filter")
    menu_gi_max = mf4.slider("Max GI", 10, 100, 100, key="menu_gi_max_slider")

    hf_map = {
        "High Protein":      lambda d: d["protein"] > 8,
        "Low GI":            lambda d: (d.get("gi") or 100) < 55,
        "High Fiber":        lambda d: d.get("fiber",0) > 3,
        "Low Calorie":       lambda d: d["kcal"] < 200,
        "Diabetic Friendly": lambda d: (d.get("gi") or 100) < 55 and d.get("fiber",0) > 2,
    }

    for meal_type, dishes in CURATED_MENU.items():
        filtered = list(dishes)
        if menu_search:
            q = menu_search.lower()
            filtered = [d for d in filtered if q in d["name"].lower() or any(q in i.lower() for i in d.get("ingredients",[]))]
        if menu_diet == "Vegetarian":
            filtered = [d for d in filtered if d["diet"] == "vegetarian"]
        elif menu_diet == "Non-Vegetarian":
            filtered = [d for d in filtered if d["diet"] == "non-vegetarian"]
        if menu_health != "All" and menu_health in hf_map:
            fn = hf_map[menu_health]
            filtered = [d for d in filtered if fn(d)]
        filtered = [d for d in filtered if (d.get("gi") or 0) <= menu_gi_max or d.get("gi") is None]
        if not filtered:
            continue

        with st.expander(f"{meal_type} — {len(filtered)} dishes", expanded=True):
            cols = st.columns(3)
            for i, d in enumerate(filtered):
                with cols[i % 3]:
                    # ── FIX: Build all conditional HTML strings BEFORE the f-string ──
                    is_veg     = d["diet"] == "vegetarian"
                    hs         = d.get("healthy_score", 5)
                    hc         = health_color(hs)
                    vtag       = veg_tag(is_veg)
                    gtag       = gi_tag(d.get("gi"))
                    tags_html  = "".join(course_tag(t) for t in d.get("tags",[])[:2])
                    ings_str   = ", ".join(d.get("ingredients",["—"])[:4])
                    ings_etc   = "…" if len(d.get("ingredients",[])) > 4 else ""
                    prot_str   = f"{d['protein']:.0f}"
                    carbs_str  = f"{d['carbs']:.0f}"
                    fiber_str  = f"{d.get('fiber',0):.0f}"

                    card_html = (
                        f'<div class="dish-card">'
                        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">'
                        f'<div style="font-size:14px;font-weight:700;line-height:1.3;flex:1">{d["name"]}</div>'
                        f'<div style="background:rgba(255,255,255,.06);border-radius:8px;padding:4px 8px;text-align:center;margin-left:8px;flex-shrink:0">'
                        f'<div style="font-family:Playfair Display,serif;font-size:16px;font-weight:700;color:{hc}">{hs}</div>'
                        f'<div style="font-size:8px;color:var(--muted)">HEALTH</div></div></div>'
                        f'<div style="margin-bottom:8px">{vtag}{gtag}{tags_html}</div>'
                        f'<div style="display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap">'
                        f'{mp("k",f"{d[chr(107)+(chr(99)+chr(97)+chr(108))]} kcal")}'
                        f'{mp("p",f"P {prot_str}g")}'
                        f'{mp("c",f"C {carbs_str}g")}'
                        f'{mp("f",f"🌾 {fiber_str}g fiber")}'
                        f'</div>'
                        f'<div style="font-size:10px;color:var(--muted)">🧂 {ings_str}{ings_etc}</div>'
                        f'</div>'
                    )
                    # Simpler direct approach - no chr() tricks needed
                    card_html2 = (
                        '<div class="dish-card">'
                        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">'
                        '<div style="font-size:14px;font-weight:700;line-height:1.3;flex:1">' + d["name"] + '</div>'
                        '<div style="background:rgba(255,255,255,.06);border-radius:8px;padding:4px 8px;text-align:center;margin-left:8px;flex-shrink:0">'
                        '<div style="font-family:Playfair Display,serif;font-size:16px;font-weight:700;color:' + hc + '">' + str(hs) + '</div>'
                        '<div style="font-size:8px;color:var(--muted)">HEALTH</div></div></div>'
                        '<div style="margin-bottom:8px">' + vtag + gtag + tags_html + '</div>'
                        '<div style="display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap">'
                        + mp("k", str(d["kcal"]) + " kcal")
                        + mp("p", "P " + prot_str + "g")
                        + mp("c", "C " + carbs_str + "g")
                        + mp("f", "🌾 " + fiber_str + "g fiber")
                        + '</div>'
                        '<div style="font-size:10px;color:var(--muted)">🧂 ' + ings_str + ings_etc + '</div>'
                        '</div>'
                    )
                    st.markdown(card_html2, unsafe_allow_html=True)

                    btn_key = f"mlog_{meal_type}_{i}"
                    if st.button("+ Log to Today", key=btn_key, use_container_width=True):
                        d2 = dict(d)
                        d2["serving"]   = 1.0
                        d2["logged_at"] = datetime.datetime.now().strftime("%H:%M")
                        st.session_state["meal_log"].setdefault(today_str, {}).setdefault(meal_type, []).append(d2)
                        st.success(f"✅ {d['name']} logged!")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RECOMMENDATIONS  (BUG FIX: same safe HTML building)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(
        '<div class="eyebrow">Smart Suggestions</div>'
        '<div class="h1">Personalised Recommendations ⭐</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">Dishes ranked for your goal, diet, health conditions and region.</p>',
        unsafe_allow_html=True
    )
    goal_icons = {"Lose Weight":"🏃","Lose Weight (Fast)":"⚡","Maintain Weight":"⚖️","Gain Muscle":"💪","Gain Weight":"📈"}
    cond_str   = (" · " + ", ".join(conditions)) if conditions else ""
    ctx_html   = (
        '<div style="background:linear-gradient(135deg,rgba(255,107,43,.1),rgba(245,166,35,.06));'
        'border:1px solid rgba(255,107,43,.25);border-radius:14px;padding:20px;margin-bottom:24px">'
        '<div style="display:flex;align-items:center;gap:12px">'
        '<span style="font-size:36px">' + goal_icons.get(goal,"🎯") + '</span>'
        '<div><div style="font-family:Playfair Display,serif;font-size:20px;font-weight:700">' + goal + '</div>'
        '<div style="font-size:12px;color:var(--muted);margin-top:4px">'
        + f"{targets['kcal']:,} kcal · {targets['prot']}g protein · {diet} · {region} India" + cond_str
        + '</div></div></div></div>'
    )
    st.markdown(ctx_html, unsafe_allow_html=True)

    for meal_type in CURATED_MENU:
        recs = get_recommended_dishes(profile, targets, meal_type, n=4)
        if not recs: continue
        st.markdown(f"### {meal_type}")
        rc = st.columns(4)
        for i, d in enumerate(recs):
            with rc[i]:
                hs     = d.get("healthy_score", 5)
                hc     = health_color(hs)
                vtag   = veg_tag(d["diet"] == "vegetarian")
                gtag   = gi_tag(d.get("gi"))
                reasons = []
                if d["protein"] > 8:            reasons.append("High Protein")
                if (d.get("gi") or 100) < 55:   reasons.append("Low GI")
                if d.get("fiber",0) > 3:         reasons.append("High Fibre")
                if d["kcal"] < 200:              reasons.append("Low Cal")
                if hs >= 9:                      reasons.append("Top Pick")
                badges_html = " ".join(reason_badge(r) for r in reasons[:3])
                prot_s  = f"{d['protein']:.0f}"
                carbs_s = f"{d['carbs']:.0f}"
                fib_s   = f"{d.get('fiber',0):.0f}"

                rc_html = (
                    '<div class="rc">'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
                    '<div style="font-size:13px;font-weight:700;line-height:1.3">' + d["name"] + '</div>'
                    '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:' + hc + '">' + str(hs) + '/10</div>'
                    '</div>'
                    + vtag + gtag
                    + '<div style="margin:8px 0;display:flex;flex-wrap:wrap;gap:4px">' + badges_html + '</div>'
                    + '<div style="font-size:11px;color:var(--muted)">'
                    + str(d["kcal"]) + ' kcal · P:' + prot_s + 'g · C:' + carbs_s + 'g · 🌾' + fib_s + 'g</div>'
                    + '</div>'
                )
                st.markdown(rc_html, unsafe_allow_html=True)
                if st.button("✚ Add Today", key=f"rec_{meal_type}_{i}", use_container_width=True):
                    d2 = dict(d); d2["serving"]=1.0; d2["logged_at"]=datetime.datetime.now().strftime("%H:%M")
                    st.session_state["meal_log"].setdefault(today_str,{}).setdefault(meal_type,[]).append(d2)
                    st.success(f"✅ {d['name']} added!"); st.rerun()
        st.divider()

    st.markdown("### 💡 Evidence-Based Nutrition Tips")
    tips = [
        ("🥣","Lead with Protein","Begin every meal with protein — dal, paneer, eggs, legumes. Reduces hunger hormone ghrelin and prevents post-meal spikes."),
        ("🌾","Choose Whole Grains","Replace maida with whole wheat. Mix bajra/jowar/ragi with rice — 2× more fibre, lower GI, higher minerals."),
        ("🫙","Fermented Foods Daily","Idli, dosa batter, curd, kanji — probiotic powerhouses. Gut health directly affects immunity, mood and metabolism."),
        ("🥗","Half Plate Vegetables","At least 50% of your plate: vegetables. Use the Indian thali model — variety is key."),
        ("⏰","Eat on a Fixed Schedule","Same meal times daily → regulated insulin → better metabolism. Ayurveda and circadian biology agree."),
        ("🚫","Limit Ultra-Processed","Packaged namkeen, biscuits, instant noodles: calorie-dense, nutrient-empty. Limit to max 1x/week."),
    ]
    tc = st.columns(3)
    for i, (icon, title, text) in enumerate(tips):
        with tc[i%3]:
            st.markdown(
                '<div class="card"><div style="font-size:28px;margin-bottom:8px">' + icon + '</div>'
                '<div style="font-size:13px;font-weight:700;margin-bottom:6px">' + title + '</div>'
                '<div style="font-size:11px;color:var(--muted);line-height:1.6">' + text + '</div></div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WEEKLY PLANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(
        '<div class="eyebrow">Meal Planning</div>'
        '<div class="h1">Weekly Planner 📅</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">Plan your entire week in advance with healthy traditional dishes.</p>',
        unsafe_allow_html=True
    )
    wk_off   = st.selectbox("Week", [0,-7,7], format_func=lambda x:{0:"This week",-7:"Last week",7:"Next week"}[x], key="wk_offset")
    wk_start = today + datetime.timedelta(days=wk_off - today.weekday())
    week_days = [wk_start + datetime.timedelta(days=i) for i in range(7)]

    gc1, gc2, gc3 = st.columns([2,1,1])
    with gc1:
        if st.button("🔀 Auto-Generate Healthy Week", key="wk_gen"):
            rng = random.Random(42)
            for d in week_days:
                ds = d.isoformat()
                st.session_state["weekly_plan"][ds] = {}
                for mt, dishes in CURATED_MENU.items():
                    pool = [x for x in dishes if (profile["diet"]=="Non-Vegetarian" or x["diet"]=="vegetarian") and x.get("healthy_score",5)>=7]
                    if pool: st.session_state["weekly_plan"][ds][mt] = [rng.choice(pool)]
            st.success("✅ Healthy week generated!"); st.rerun()
    with gc2:
        if st.button("🗑 Clear Week", key="wk_clr"):
            for d in week_days: st.session_state["weekly_plan"].pop(d.isoformat(), None)
            st.rerun()
    with gc3:
        if st.button("📋 Copy to Log", key="wk_copy"):
            for d in week_days:
                ds   = d.isoformat()
                plan = st.session_state["weekly_plan"].get(ds, {})
                for mt, dishes in plan.items():
                    for dish in dishes:
                        d2 = dict(dish); d2["serving"]=1.0; d2["logged_at"]="Planned"
                        st.session_state["meal_log"].setdefault(ds,{}).setdefault(mt,[]).append(d2)
            st.success("✅ Copied to meal log!")

    st.divider()
    dcols = st.columns(7)
    for ci, (col, day) in enumerate(zip(dcols, week_days)):
        ds = day.isoformat()
        dp = st.session_state["weekly_plan"].get(ds, {})
        dk = sum(float(d.get("kcal",0) or 0) for ms in dp.values() for d in ms)
        is_today_day = day == today
        border_style = "1px solid #FF6B2B" if is_today_day else "1px solid rgba(255,248,240,.08)"
        day_color    = "#FF6B2B" if is_today_day else "var(--muted)"
        num_color    = "#FF6B2B" if is_today_day else "#FFF8F0"
        kcal_line    = f'<div style="font-size:11px;color:#FF6B2B;margin-top:4px;font-weight:600">{dk:.0f} kcal</div>' if dk else '<div style="font-size:10px;color:rgba(255,248,240,.2);margin-top:4px">No plan</div>'
        with col:
            st.markdown(
                '<div style="background:#16162A;border:' + border_style + ';border-radius:12px;padding:12px;margin-bottom:8px">'
                '<div style="font-family:Space Mono,monospace;font-size:9px;text-transform:uppercase;color:' + day_color + '">' + day.strftime("%a") + '</div>'
                '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:' + num_color + '">' + str(day.day) + '</div>'
                '<div style="font-size:10px;color:var(--muted)">' + day.strftime("%b") + '</div>'
                + kcal_line + '</div>',
                unsafe_allow_html=True
            )
            for mt_key, mt_dishes in dp.items():
                for d in mt_dishes:
                    nm = d["name"][:16] + ("…" if len(d["name"])>16 else "")
                    st.markdown(
                        '<div style="font-size:10px;background:rgba(255,107,43,.07);border-radius:6px;padding:4px 8px;margin-bottom:4px;line-height:1.3">'
                        + mt_key.split()[0] + " " + nm + '</div>',
                        unsafe_allow_html=True
                    )

    st.divider()
    st.markdown("### 🗓 Plan a Specific Day")
    detail_day = st.date_input("Select day", value=today, key="wk_detail_day")
    dd_str = detail_day.isoformat()
    if dd_str not in st.session_state["weekly_plan"]: st.session_state["weekly_plan"][dd_str] = {}

    for mt in CURATED_MENU:
        current = st.session_state["weekly_plan"][dd_str].get(mt, [])
        st.markdown(f"**{mt}**")
        mc1, mc2 = st.columns([3,1])
        with mc1:
            opts = ["-- Add dish --"] + [d["name"] for d in CURATED_MENU[mt] if profile["diet"]=="Non-Vegetarian" or d["diet"]=="vegetarian"]
            sel  = st.selectbox("", opts, key=f"wk_{dd_str}_{mt}", label_visibility="collapsed")
        with mc2:
            if st.button("Add", key=f"wkadd_{dd_str}_{mt}") and sel != "-- Add dish --":
                found = next((d for d in CURATED_MENU[mt] if d["name"]==sel), None)
                if found: st.session_state["weekly_plan"][dd_str].setdefault(mt,[]).append(dict(found)); st.rerun()
        for idx, d in enumerate(current):
            dc1, dc2 = st.columns([5,1])
            with dc1:
                st.markdown(
                    '<div class="lr"><span style="font-size:13px;font-weight:600">' + d["name"] + '</span>'
                    + mp("k", str(d["kcal"]) + " kcal") + '</div>',
                    unsafe_allow_html=True
                )
            with dc2:
                if st.button("×", key=f"wkrm_{dd_str}_{mt}_{idx}"):
                    st.session_state["weekly_plan"][dd_str][mt].pop(idx); st.rerun()

    plan_dishes = [d for ms in st.session_state["weekly_plan"].get(dd_str,{}).values() for d in ms]
    if plan_dishes:
        st.divider()
        ps1,ps2,ps3,ps4 = st.columns(4)
        pk = sum(float(d.get("kcal",0) or 0) for d in plan_dishes)
        pp = sum(float(d.get("protein",0) or 0) for d in plan_dishes)
        pc = sum(float(d.get("carbs",0) or 0) for d in plan_dishes)
        pf = sum(float(d.get("fat",0) or 0) for d in plan_dishes)
        ps1.metric("Planned Cal", f"{pk:.0f}", f"target {targets['kcal']}")
        ps2.metric("Protein",     f"{pp:.0f}g", f"{targets['prot']}g")
        ps3.metric("Carbs",       f"{pc:.0f}g", f"{targets['carbs']}g")
        ps4.metric("Fat",         f"{pf:.0f}g", f"{targets['fat']}g")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SHOPPING LIST
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(
        '<div class="eyebrow">Grocery Planning</div>'
        '<div class="h1">Shopping List 🛒</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">Auto-generated from your weekly plan. Check off as you shop.</p>',
        unsafe_allow_html=True
    )
    sl1, sl2, sl3 = st.columns([2,1,1])
    with sl1:
        sl_range = st.selectbox("Generate for", ["This week's plan","Today's log","Next 3 days"], key="sl_range")
    with sl2:
        if st.button("🔄 Generate", key="sl_gen"):
            all_ing = defaultdict(int)
            if "week" in sl_range.lower() or "3 days" in sl_range.lower():
                dc = 7 if "week" in sl_range.lower() else 3
                for i in range(dc):
                    d = (today + datetime.timedelta(days=i)).isoformat()
                    for dishes in st.session_state["weekly_plan"].get(d,{}).values():
                        for dish in dishes:
                            for ing in dish.get("ingredients",[]): all_ing[ing.strip()] += 1
            else:
                for dishes in st.session_state["meal_log"].get(today_str,{}).values():
                    for dish in dishes:
                        for ing in dish.get("ingredients",[]): all_ing[ing.strip()] += 1
            nl = {}
            for ing, cnt in all_ing.items():
                nl[ing] = {"qty": cnt, "checked": st.session_state["shopping_list"].get(ing,{}).get("checked",False)}
            st.session_state["shopping_list"] = nl
            st.success(f"✅ {len(nl)} items!"); st.rerun()
    with sl3:
        if st.button("🗑 Clear", key="sl_clr"): st.session_state["shopping_list"]={};st.rerun()

    if st.session_state["shopping_list"]:
        by_cat = defaultdict(list)
        for ing, info in st.session_state["shopping_list"].items():
            by_cat[get_ingredient_category(ing)].append((ing,info))
        chk = sum(1 for i in st.session_state["shopping_list"].values() if i.get("checked"))
        tot = len(st.session_state["shopping_list"])
        st.markdown(
            '<div style="background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:12px;padding:16px;margin-bottom:12px">'
            '<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
            '<span style="font-size:13px;font-weight:600">Shopping Progress</span>'
            '<span style="font-family:Space Mono,monospace;font-size:12px;color:#FF6B2B">' + str(chk) + "/" + str(tot) + " items</span>"
            '</div></div>',
            unsafe_allow_html=True
        )
        st.progress(chk/tot if tot else 0)
        cat_icons = {"Dairy & Eggs":"🥛","Lentils & Legumes":"🫘","Grains & Flours":"🌾","Vegetables":"🥦","Meat & Fish":"🍗","Spices & Condiments":"🌶️","Nuts & Seeds":"🥜","Sweeteners":"🍯","Oils & Fats":"🫙","Fresh Herbs":"🌿","Beverages":"☕","Specialty/Other":"🧪","Others":"📦"}
        for cat, items in sorted(by_cat.items()):
            icon = cat_icons.get(cat,"📦")
            with st.expander(f"{icon} {cat} ({len(items)})", expanded=True):
                for ing, info in items:
                    safe_key = re.sub(r'[^a-zA-Z0-9_]','_', ing)
                    checked  = st.checkbox(
                        ing + ("  · ×"+str(info["qty"])+" recipes" if info["qty"]>1 else ""),
                        value=info.get("checked",False), key="slc_"+safe_key
                    )
                    st.session_state["shopping_list"][ing]["checked"] = checked
        st.divider()
        if st.button("📋 Export as Text", key="sl_exp"):
            lines = ["🛒 NOURISH SHOPPING LIST","="*30]
            for cat, items in sorted(by_cat.items()):
                icon = cat_icons.get(cat,"📦")
                lines.append("\n" + icon + " " + cat)
                for ing, info in items:
                    lines.append("  " + ("☑ " if info.get("checked") else "☐ ") + ing)
            st.text_area("Copy this list", "\n".join(lines), height=300, key="sl_text")
    else:
        st.markdown(
            '<div style="background:rgba(255,248,240,.03);border:1.5px dashed rgba(255,248,240,.1);border-radius:14px;padding:48px;text-align:center">'
            '<div style="font-size:48px;margin-bottom:12px">🛒</div>'
            '<div style="font-size:16px;font-weight:600;margin-bottom:8px">Shopping list is empty</div>'
            '<div style="font-size:13px;color:var(--muted)">Create a Weekly Plan first, then click "Generate"</div></div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AI HEALTH ADVISOR  (NEW MAJOR FEATURE)
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown(
        '<div class="eyebrow">Powered by AI</div>'
        '<div class="h1">AI Health Advisor 🤖</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">Personalised health, diet, nutrient & exercise plans — based on your profile.</p>',
        unsafe_allow_html=True
    )

    ai_tab1, ai_tab2, ai_tab3, ai_tab4, ai_tab5 = st.tabs([
        "📊 Health Plan", "🏋️ Exercise Plan", "💬 Ask AI", "🧬 Body Analysis", "🍎 Food Science"
    ])

    # ── AI Tab 1: Full Health Plan ─────────────────────────────────────────
    with ai_tab1:
        st.markdown("#### Your AI-Generated Health Plan")
        today_log_ai = st.session_state["meal_log"].get(today_str, {})
        ai_plan = generate_ai_health_plan(profile, targets, today_log_ai)

        # BMI Section
        bmi_data = ai_plan["bmi"]
        st.markdown(
            '<div class="ai-box">'
            '<div class="ai-section">'
            '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;margin-bottom:10px">⚖️ ' + bmi_data["title"] + '</div>'
            '<div>' + bmi_data["content"].replace("**","<strong>").replace("**","</strong>") + '</div>'
            '<div style="margin-top:10px;padding:10px;background:rgba(255,248,240,.04);border-radius:8px;font-size:12px;color:var(--muted)">' + bmi_data["detail"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

        # Diet Plan Section
        diet_data = ai_plan["diet"]
        plan_rows = "".join(
            f'<div style="padding:10px 0;border-bottom:1px solid rgba(255,248,240,.05)">'
            f'<div style="font-size:12px;font-weight:700;color:#FF6B2B;margin-bottom:4px">{meal}</div>'
            f'<div style="font-size:12px;color:var(--muted);line-height:1.6">{desc}</div>'
            f'</div>'
            for meal, desc in diet_data["plan"]
        )
        st.markdown(
            '<div class="ai-box" style="margin-top:12px">'
            '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;margin-bottom:12px">🗓️ ' + diet_data["title"] + '</div>'
            + plan_rows +
            '</div>',
            unsafe_allow_html=True
        )

        # Medical Conditions
        med_data = ai_plan["medical"]
        if med_data["items"]:
            med_rows = "".join(
                f'<div class="ai-section">'
                f'<div style="font-size:14px;font-weight:700;margin-bottom:8px">{icon} {title}</div>'
                f'<div style="font-size:12px;color:var(--muted);line-height:1.8">{text}</div>'
                f'</div>'
                for icon, title, text in med_data["items"]
            )
            st.markdown(
                '<div class="ai-box" style="margin-top:12px">'
                '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;margin-bottom:12px">🏥 ' + med_data["title"] + '</div>'
                + med_rows +
                '</div>',
                unsafe_allow_html=True
            )

        # Nutrient Gaps
        nut_data = ai_plan["nutrients"]
        nut_rows = "".join(
            f'<div class="ai-section">'
            f'<div style="font-size:13px;font-weight:700;margin-bottom:6px">{icon} {name} — <span style="color:#F5A623">{reason}</span></div>'
            f'<div style="font-size:12px;color:var(--muted);line-height:1.7">{detail}</div>'
            f'</div>'
            for name, icon, reason, detail in nut_data["items"]
        )
        st.markdown(
            '<div class="ai-box" style="margin-top:12px">'
            '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;margin-bottom:12px">🧬 ' + nut_data["title"] + '</div>'
            + nut_rows +
            '</div>',
            unsafe_allow_html=True
        )

        # Today's gaps
        today_data = ai_plan["today"]
        gap_rows = "".join(
            f'<div style="padding:8px 0;border-bottom:1px solid rgba(255,248,240,.05);font-size:12px;color:var(--muted)">• {item}</div>'
            for item in today_data["items"]
        )
        st.markdown(
            '<div class="ai-box" style="margin-top:12px">'
            '<div style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;margin-bottom:10px">📈 ' + today_data["title"] + '</div>'
            + gap_rows +
            '</div>',
            unsafe_allow_html=True
        )

    # ── AI Tab 2: Exercise Plan ────────────────────────────────────────────
    with ai_tab2:
        st.markdown("#### 🏋️ Your Personalised Exercise Plan")
        ex_plan = EXERCISE_PLANS.get(goal, EXERCISE_PLANS["Maintain Weight"])
        st.markdown(alert("info", "💡 " + ex_plan["overview"]), unsafe_allow_html=True)

        weekly_burn = sum(d["calories_burned"] for d in ex_plan["days"])
        ex1,ex2,ex3 = st.columns(3)
        ex1.metric("Weekly Calorie Burn", f"{weekly_burn:,}", "from exercise")
        ex2.metric("Exercise Days", "6 days", "1 rest day")
        ex3.metric("Net Weekly Deficit" if "Lose" in goal else "Net Weekly Surplus",
                   f"{abs(GOAL_DELTA.get(goal,0)*7 + weekly_burn):,}" if "Lose" in goal else f"{weekly_burn:,}",
                   "combined diet + exercise")
        st.divider()

        # Today's exercise highlight
        today_idx = today.weekday()
        today_ex  = ex_plan["days"][today_idx]
        today_type_color = TYPE_COLORS.get(today_ex["type"], "#888")
        st.markdown(
            '<div style="background:linear-gradient(135deg,rgba(255,107,43,.12),rgba(0,212,255,.06));'
            'border:1px solid rgba(255,107,43,.3);border-radius:14px;padding:20px;margin-bottom:20px">'
            '<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#FF6B2B;margin-bottom:6px">TODAY — ' + today_ex["day"].upper() + '</div>'
            '<div style="font-family:Playfair Display,serif;font-size:24px;font-weight:700;margin-bottom:8px">' + today_ex["activity"] + '</div>'
            '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px">'
            '<span style="background:' + today_type_color + '22;color:' + today_type_color + ';padding:4px 12px;border-radius:10px;font-size:11px;font-weight:700">' + today_ex["type"] + '</span>'
            '<span style="color:var(--muted);font-size:12px">⏱ ' + today_ex["duration"] + '</span>'
            '<span style="color:var(--muted);font-size:12px">💪 ' + today_ex["intensity"] + '</span>'
            '<span style="color:#FF6B2B;font-size:12px">🔥 ' + str(today_ex["calories_burned"]) + ' kcal</span>'
            '</div>'
            '<div style="font-size:12px;color:var(--muted);background:rgba(255,248,240,.04);border-radius:8px;padding:10px">💡 ' + today_ex["tips"] + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Full week view
        st.markdown("**📅 Full Week Schedule**")
        for ex_day in ex_plan["days"]:
            tc_ = TYPE_COLORS.get(ex_day["type"], "#888")
            is_td = ex_day["day"] == today.strftime("%A")
            bdr   = "1px solid rgba(255,107,43,.4)" if is_td else "1px solid rgba(255,248,240,.07)"
            st.markdown(
                '<div class="ex-card" style="border:' + bdr + '">'
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">'
                '<div>'
                '<div style="font-family:Space Mono,monospace;font-size:9px;text-transform:uppercase;color:' + tc_ + ';margin-bottom:4px">' + ("🔴 TODAY — " if is_td else "") + ex_day["day"].upper() + ' — ' + ex_day["type"] + '</div>'
                '<div style="font-size:14px;font-weight:700">' + ex_day["activity"] + '</div>'
                '<div style="font-size:11px;color:var(--muted);margin-top:4px">💡 ' + ex_day["tips"] + '</div>'
                '</div>'
                '<div style="text-align:right;flex-shrink:0">'
                '<div style="font-size:11px;color:var(--muted)">⏱ ' + ex_day["duration"] + '</div>'
                '<div style="font-size:11px;color:var(--muted)">' + ex_day["intensity"] + '</div>'
                '<div style="font-size:13px;font-weight:700;color:#FF6B2B;margin-top:4px">🔥 ' + str(ex_day["calories_burned"]) + ' kcal</div>'
                '</div></div></div>',
                unsafe_allow_html=True
            )

        # Exercise science tips
        st.divider()
        st.markdown("**🧬 Exercise Science for Indians**")
        ex_tips = [
            ("🌅","Best exercise time","Between 6-9am on empty stomach for fat loss. Post-meal walk (10 min after dinner) reduces blood sugar spike by 22%."),
            ("🧘","Yoga as base","Surya Namaskar: 12 rounds = 156 calories + full-body stretch + mental calm. Scientific evidence backs yoga for PCOS, hypertension, diabetes management."),
            ("💧","Hydrate smart","Drink 400ml water 2hrs before exercise. 200ml every 20 min during workout. Coconut water > sports drinks for Indian climate."),
            ("🍌","Pre-workout fuel","1 banana + sattu drink = perfect natural pre-workout. Avoid heavy meals 2hrs before. Dal-rice 3hrs before endurance exercise."),
            ("😴","Sleep = recovery","Muscles grow during sleep, not exercise. 7-8hrs non-negotiable. Poor sleep increases cortisol → belly fat → undoes exercise benefit."),
            ("📊","Track progress","Measure waist (not just weight). Muscle weighs more than fat. Monthly measurements beat daily weigh-ins for motivation."),
        ]
        et_cols = st.columns(3)
        for i, (icon, title, text) in enumerate(ex_tips):
            with et_cols[i%3]:
                st.markdown(
                    '<div class="card"><div style="font-size:24px;margin-bottom:6px">' + icon + '</div>'
                    '<div style="font-size:13px;font-weight:700;margin-bottom:4px">' + title + '</div>'
                    '<div style="font-size:11px;color:var(--muted);line-height:1.6">' + text + '</div></div>',
                    unsafe_allow_html=True
                )

    # ── AI Tab 3: Ask AI ───────────────────────────────────────────────────
    with ai_tab3:
        st.markdown("#### 💬 Ask Your AI Health Coach")
        st.markdown(
            '<div class="ab ab-i">This AI Health Coach uses built-in Indian nutrition intelligence. '
            'For Claude AI responses, enter your Anthropic API key below (optional).</div>',
            unsafe_allow_html=True
        )

        # Preset questions
        st.markdown("**Quick Questions:**")
        preset_qs = [
            "What should I eat to lose belly fat with Indian food?",
            "Best protein sources for vegetarians in India?",
            "How to reduce blood sugar with Indian diet?",
            "What is the best pre-workout meal for Indian vegetarians?",
            "How many chapatis should I eat per day for weight loss?",
            "Which Indian breakfast is best for weight loss?",
        ]
        pq_cols = st.columns(2)
        for i, pq in enumerate(preset_qs):
            with pq_cols[i%2]:
                if st.button(pq, key=f"pq_{i}", use_container_width=True):
                    st.session_state["ai_chat"].append({"role":"user","content":pq})
                    st.rerun()

        st.divider()
        # Chat interface
        user_q = st.text_area("Or type your health question:", placeholder="e.g. I have PCOS and want to lose weight. What Indian foods should I eat?", key="ai_user_q", height=80)

        # Optional API key
        with st.expander("🔑 Claude AI API Key (Optional — for smarter personalised answers)"):
            api_key_input = st.text_input("Anthropic API Key", type="password", key="api_key_input", help="Get free key at console.anthropic.com")
            if api_key_input:
                st.markdown(alert("good","✅ API key entered. Questions will be answered by Claude AI."), unsafe_allow_html=True)

        col_ask, col_clear = st.columns([3,1])
        with col_ask:
            if st.button("🤖 Get AI Answer", key="ai_ask_btn") and user_q.strip():
                st.session_state["ai_chat"].append({"role":"user","content":user_q.strip()})
                st.rerun()
        with col_clear:
            if st.button("🗑 Clear Chat", key="ai_clear"):
                st.session_state["ai_chat"] = []; st.rerun()

        # Display chat history + generate answers
        for idx, msg in enumerate(st.session_state["ai_chat"]):
            if msg["role"] == "user":
                st.markdown(
                    '<div style="background:rgba(255,107,43,.08);border:1px solid rgba(255,107,43,.2);'
                    'border-radius:10px;padding:12px 16px;margin:8px 0">'
                    '<div style="font-size:10px;font-weight:700;color:#FF6B2B;margin-bottom:4px;font-family:Space Mono,monospace">YOU</div>'
                    '<div style="font-size:13px">' + msg["content"] + '</div></div>',
                    unsafe_allow_html=True
                )
                # Generate answer if next message isn't already an answer
                next_idx = idx + 1
                needs_answer = (next_idx >= len(st.session_state["ai_chat"]) or
                               st.session_state["ai_chat"][next_idx]["role"] != "assistant")
                if needs_answer:
                    with st.spinner("🤖 Thinking…"):
                        api_key_val = st.session_state.get("api_key_input","").strip()
                        if api_key_val and ANTHROPIC_AVAILABLE:
                            prompt = build_claude_prompt(profile, targets, msg["content"])
                            answer = call_claude_api(prompt, api_key_val)
                        else:
                            answer = generate_rule_based_answer(msg["content"], profile, targets) if 'generate_rule_based_answer' in dir() else _rule_answer(msg["content"], profile, targets)
                    st.session_state["ai_chat"].append({"role":"assistant","content":answer})
                    st.rerun()
            else:
                st.markdown(
                    '<div class="ai-box" style="margin:8px 0">'
                    '<div style="font-size:10px;font-weight:700;color:#4ECBA0;margin-bottom:8px;font-family:Space Mono,monospace">🤖 NOURISH AI</div>'
                    '<div style="font-size:13px;line-height:1.8;white-space:pre-wrap">' + msg["content"] + '</div></div>',
                    unsafe_allow_html=True
                )

    # ── AI Tab 4: Body Analysis ────────────────────────────────────────────
    with ai_tab4:
        st.markdown("#### 🧬 Body Analysis & Metabolic Profile")
        ba1, ba2 = st.columns(2)

        with ba1:
            # BMR breakdown
            bmi_val = targets["bmi"]
            bmi_c   = targets["bmi_cat"]
            bmi_col = targets["bmi_col"]
            bp      = min(1.0, max(0, (bmi_val - 15) / 25))
            ang     = -90 + bp * 180
            rad_    = ang * math.pi / 180
            nx      = 100 + 70 * math.cos(rad_)
            ny      = 100 + 70 * math.sin(rad_)
            st.markdown(
                '<div style="text-align:center;background:#16162A;border:1px solid rgba(255,248,240,.08);border-radius:14px;padding:24px;margin-bottom:16px">'
                '<svg viewBox="0 0 200 120" width="200">'
                '<defs><linearGradient id="bmigrad" x1="0%" y1="0%" x2="100%" y2="0%">'
                '<stop offset="0%" style="stop-color:#00D4FF"/><stop offset="30%" style="stop-color:#4ECBA0"/>'
                '<stop offset="55%" style="stop-color:#F5A623"/><stop offset="75%" style="stop-color:#FF6B2B"/>'
                '<stop offset="100%" style="stop-color:#FF4B6E"/></linearGradient></defs>'
                '<path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,248,240,0.06)" stroke-width="14" stroke-linecap="round"/>'
                '<path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#bmigrad)" stroke-width="14" stroke-linecap="round" opacity=".5"/>'
                '<line x1="100" y1="100" x2="' + f"{nx:.1f}" + '" y2="' + f"{ny:.1f}" + '" stroke="' + bmi_col + '" stroke-width="3" stroke-linecap="round"/>'
                '<circle cx="100" cy="100" r="6" fill="' + bmi_col + '"/>'
                '</svg>'
                '<div style="font-family:Playfair Display,serif;font-size:42px;font-weight:700;color:' + bmi_col + '">' + str(bmi_val) + '</div>'
                '<div style="font-size:14px;color:var(--muted)">' + bmi_c + '</div>'
                '<div style="font-size:11px;color:rgba(255,248,240,.3);margin-top:6px">Healthy: 18.5–24.9</div>'
                '</div>',
                unsafe_allow_html=True
            )

            # Metabolic profile
            st.markdown("**Metabolic Profile**")
            protein_need = round(profile["weight"] * (1.6 if "Muscle" in goal else 1.2 if "Lose" in goal else 1.0))
            water_need   = targets["water"]
            ideal_weight_low  = round(18.5 * (profile["height"]/100)**2, 1)
            ideal_weight_high = round(24.9 * (profile["height"]/100)**2, 1)
            weight_to_lose = round(profile["weight"] - ideal_weight_high, 1) if profile["weight"] > ideal_weight_high else 0
            weeks_to_goal  = round(abs(weight_to_lose) / 0.5) if weight_to_lose > 0 else 0

            meta_items = [
                ("Basal Metabolic Rate (BMR)", f"{targets['bmr']:,} kcal", "Calories burned at complete rest"),
                ("Total Daily Energy (TDEE)",  f"{targets['tdee']:,} kcal", "With your activity level"),
                ("Calorie Target",             f"{targets['kcal']:,} kcal", f"TDEE {'+' if GOAL_DELTA.get(goal,0)>0 else ''}{GOAL_DELTA.get(goal,0)} for {goal}"),
                ("Protein Need",               f"{protein_need}g/day",      "Based on goal and bodyweight"),
                ("Water Need",                 f"{water_need:,}ml/day",     "35ml × bodyweight + 200ml"),
                ("Ideal Weight Range",         f"{ideal_weight_low}–{ideal_weight_high}kg", "BMI 18.5–24.9 for your height"),
                ("To reach ideal weight",      f"{weight_to_lose}kg to lose" if weight_to_lose>0 else "Within healthy range", f"~{weeks_to_goal} weeks at 0.5kg/week" if weeks_to_goal>0 else "Maintain current weight"),
            ]
            for label, val, note in meta_items:
                st.markdown(
                    '<div style="display:flex;justify-content:space-between;align-items:flex-start;padding:8px 0;border-bottom:1px solid rgba(255,248,240,.05)">'
                    '<div><div style="font-size:12px;font-weight:600">' + label + '</div>'
                    '<div style="font-size:10px;color:var(--muted)">' + note + '</div></div>'
                    '<div style="font-family:Playfair Display,serif;font-size:14px;font-weight:700;color:#FF6B2B">' + val + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

        with ba2:
            st.markdown("**Macro Distribution**")
            total_cals = targets["kcal"]
            prot_cals  = round(targets["prot"] * 4)
            carb_cals  = round(targets["carbs"] * 4)
            fat_cals   = round(targets["fat"] * 9)
            prot_pct   = round(prot_cals/total_cals*100)
            carb_pct   = round(carb_cals/total_cals*100)
            fat_pct    = 100 - prot_pct - carb_pct

            for label, grams, cals, pct, col_ in [
                ("Protein", targets['prot'], prot_cals, prot_pct, "#FF6B2B"),
                ("Carbohydrates", targets['carbs'], carb_cals, carb_pct, "#F5A623"),
                ("Fat", targets['fat'], fat_cals, fat_pct, "#4ECBA0"),
            ]:
                st.markdown(
                    '<div style="background:#16162A;border:1px solid rgba(255,248,240,.07);border-radius:10px;padding:14px;margin-bottom:8px">'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
                    '<span style="font-size:13px;font-weight:700">' + label + '</span>'
                    '<span style="font-family:Playfair Display,serif;font-size:18px;font-weight:700;color:' + col_ + '">' + str(pct) + '%</span>'
                    '</div>'
                    '<div style="height:6px;background:rgba(255,255,255,.06);border-radius:3px;margin-bottom:8px">'
                    '<div style="height:100%;width:' + str(pct) + '%;background:' + col_ + ';border-radius:3px"></div>'
                    '</div>'
                    '<div style="display:flex;justify-content:space-between;font-size:11px;color:var(--muted)">'
                    '<span>' + str(grams) + 'g</span><span>' + str(cals) + ' kcal</span>'
                    '</div></div>',
                    unsafe_allow_html=True
                )

            st.divider()
            st.markdown("**Goal Analysis**")
            goal_details = {
                "Lose Weight":        ("Aim: −0.5kg/week","Sustainable fat loss preserves muscle. Crash diets cause muscle loss and rebound weight gain."),
                "Lose Weight (Fast)": ("Aim: −0.75kg/week","Aggressive cut. Ensure adequate protein (1.6g/kg) to prevent muscle loss. Not for >8 weeks."),
                "Maintain Weight":    ("Aim: ±0kg","Focus on body composition. Replace fat with muscle. Maintain current calorie balance."),
                "Gain Muscle":        ("Aim: +0.25-0.5kg lean/week","Calorie surplus + progressive overload + 1.6-2g protein/kg. Sleep and recovery are as important as training."),
                "Gain Weight":        ("Aim: +0.5kg/week","Calorie surplus from nutritious foods. Avoid gaining mainly fat — include strength training."),
            }
            g_aim, g_text = goal_details.get(goal, ("",""))
            st.markdown(
                '<div class="ai-box">'
                '<div style="font-size:11px;font-weight:700;color:#FF6B2B;margin-bottom:6px">' + goal.upper() + ' — ' + g_aim + '</div>'
                '<div style="font-size:12px;color:var(--muted);line-height:1.7">' + g_text + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

    # ── AI Tab 5: Food Science ─────────────────────────────────────────────
    with ai_tab5:
        st.markdown("#### 🍎 Indian Food Science & Ayurveda")
        fs_sections = [
            ("🌅","Breakfast: The Agni Principle","Ayurveda says 'feed your agni (digestive fire)' in the morning. Modern science agrees: breakfast within 1hr of waking prevents cortisol spike, reduces insulin resistance, and kick-starts metabolism. Best Indian breakfasts by science: Besan chilla (best protein/calorie ratio), Daliya porridge (best GI for sustained energy), Pesarattu (highest protein among traditional breakfasts), Idli-sambar (best probiotic + protein combination)."),
            ("🥣","Dal: India's Protein Powerhouse","Dal provides all essential amino acids when eaten with rice or roti (complementary proteins). The lysine in dal + methionine in grain = complete protein. Moong dal: easiest to digest, best for sick days, lowest GI (25). Masoor dal: highest iron, best for anaemia. Urad dal: highest calcium, good for bones. Toor dal: highest protein, best for muscle building."),
            ("🌾","Millets: The Ancient Superfood","India's original grain before rice took over. Bajra: highest iron (8mg/100g vs wheat's 3.5mg). Ragi: highest calcium (344mg/100g — more than milk per gram). Jowar: highest fibre, best for diabetics. Amaranth: only grain with complete protein + calcium. Try rotating one millet per week."),
            ("🫙","Fermentation: India's Probiotic Secret","Indian fermented foods are world-class probiotics. Idli batter (fermented 8-12hrs): Lactobacillus multiplies 1000×, increases B vitamins. Kanji (fermented carrot/beetroot): rich in Lactobacillus plantarum. Traditional curd: 1 billion CFU/serving. Fermented foods reduce lactose intolerance, improve digestion, boost immunity, and even reduce anxiety (gut-brain axis)."),
            ("🌶️","Indian Spices: Medicine Cabinet in Kitchen","Turmeric: curcumin reduces inflammation = reduces joint pain, lowers cancer risk, fights depression. Absorb better with black pepper (piperine increases absorption by 2000%) and fat. Ginger: reduces nausea, lowers blood sugar, anti-inflammatory. Cinnamon: lowers post-meal blood sugar by 29%. Cardamom: lowers blood pressure. Asafoetida (hing): best natural digestive for IBS."),
            ("🥛","Dairy: The Indian Debate","Indian dairy is traditionally A2 milk (Gir cow, buffalo) which is easier to digest than A1 (Holstein cows). Curd/yogurt: best dairy form — live cultures digest lactose. Ghee: contains butyrate (gut-healing), medium-chain fatty acids, fat-soluble vitamins. NOT 'unhealthy' — 1 tsp/meal is optimal. Paneer: best protein-to-fat ratio in dairy, 18g protein/100g. Avoid: flavoured yogurt, processed cheese, UHT milk."),
        ]
        for i, (icon, title, text) in enumerate(fs_sections):
            with st.expander(icon + " " + title, expanded=(i==0)):
                st.markdown(
                    '<div style="font-size:13px;color:var(--muted);line-height:1.9;padding:4px 0">' + text + '</div>',
                    unsafe_allow_html=True
                )

# ── Rule-based answer engine for chat (no API needed) ─────────────────────
def _rule_answer(question: str, profile: dict, targets: dict) -> str:
    q = question.lower()
    goal  = profile["goal"]
    diet  = profile["diet"]
    bmi   = targets["bmi"]
    conds = profile.get("medical", [])

    if "belly fat" in q or "stomach" in q:
        return (
            "**Losing Belly Fat — Indian Diet Plan:**\n\n"
            "• Belly fat is visceral (internal) fat — most dangerous type. It responds well to:\n\n"
            "🥗 **Diet changes:**\n"
            "• Reduce white rice → switch to brown rice or bajra/jowar roti\n"
            "• Eliminate sugar: chai with jaggery → plain chai → reduce completely\n"
            "• Avoid maida: no batura, naan, biscuits, bread. Use whole wheat only\n"
            "• Add fibre: 1 bowl of dal at every meal (keeps you full 4hrs)\n"
            "• Eat methi seeds daily (1 tsp soaked overnight, eat morning) — reduces belly fat hormones\n\n"
            "🏃 **Exercise for belly fat:**\n"
            "• 45 min brisk walk every morning → single best belly fat burner\n"
            "• 10 min post-dinner walk — reduces cortisol (main belly fat hormone)\n"
            "• Core exercises: plank, crunches, bicycle kicks — 15 min/day\n\n"
            "⚠️ **Avoid:** Stress (cortisol = belly fat), poor sleep, alcohol, packaged foods"
        )
    elif "protein" in q and ("vegetarian" in q or "veg" in q):
        return (
            "**Best Vegetarian Protein Sources in India:**\n\n"
            "🏆 **Per 100g protein content:**\n"
            "• Roasted chana: 22g protein — cheapest and best\n"
            "• Paneer: 18g protein — versatile, high-quality protein\n"
            "• Moong dal (cooked): 7g protein — easiest to digest\n"
            "• Curd: 11g protein — probiotic + protein\n"
            "• Rajma: 8.7g protein — complete amino acids with rice\n"
            "• Makhana (fox nuts): 9.7g protein + 14g fibre\n"
            "• Soya chunks: 52g protein per 100g dry — best plant protein\n\n"
            "📋 **Daily protein strategy:**\n"
            "• Breakfast: moong dal chilla or besan chilla (8g)\n"
            "• Lunch: 2 bowls dal + paneer sabzi (25g)\n"
            "• Evening: roasted chana + lassi (18g)\n"
            "• Dinner: rajma/chole + roti (15g)\n"
            "• Total: ~66g — combine with dairy, seeds and varied dals to reach your target of " + str(targets["prot"]) + "g"
        )
    elif "diabetes" in q or "blood sugar" in q or "sugar" in q:
        return (
            "**Indian Diet for Blood Sugar Control:**\n\n"
            "✅ **Best Indian foods (Low GI):**\n"
            "• Bajra roti (GI 54) instead of white rice (GI 72)\n"
            "• Moong dal (GI 25) — eat daily\n"
            "• Bitter gourd (karela) — reduces blood sugar by 20%\n"
            "• Methi seeds: soak overnight, eat 1 tsp morning\n"
            "• Amla: 1 fresh amla daily (or juice) — 3× better than medicine in some studies\n"
            "• Cinnamon tea: 1/2 tsp in warm water daily\n\n"
            "❌ **Avoid completely:**\n"
            "• White rice, white bread, maida products\n"
            "• Fruit juices (eat whole fruit instead)\n"
            "• Sugar, jaggery in excess, honey\n"
            "• Potatoes, yam (high GI)\n\n"
            "🍽️ **Meal timing (critical for diabetes):**\n"
            "• Never skip meals — causes blood sugar crash and spike\n"
            "• Eat every 3 hours, small portions\n"
            "• Walk 10 min after every meal — reduces post-meal glucose by 22%"
        )
    elif "chapati" in q or "roti" in q:
        return (
            "**How Many Chapatis Per Day?**\n\n"
            "Based on your profile (Goal: " + goal + ", Target: " + str(targets["kcal"]) + " kcal):\n\n"
            "• 1 medium chapati (30g atta) = 80-90 kcal, 3g protein, 17g carbs\n\n"
            "**Recommended daily intake:**\n"
            + ("• Weight Loss: 4-6 chapatis/day (spread across meals)\n" if "Lose" in goal else
               "• Muscle Gain: 6-8 chapatis/day\n" if "Muscle" in goal else
               "• Maintenance: 6-8 chapatis/day\n")
            + "\n**Tips to make chapati healthier:**\n"
            "• Use 100% whole wheat (not maida blend)\n"
            "• Add 1 tsp methi powder or ragi to atta — boosts nutrition\n"
            "• Reduce ghee: 1/4 tsp per chapati max\n"
            "• Pair with dal (protein) + sabzi (fibre) — slows sugar absorption\n"
            "• Eat hot — resistant starch forms when chapati cools, raising GI"
        )
    elif "breakfast" in q and ("weight" in q or "lose" in q):
        return (
            "**Best Indian Breakfasts for Weight Loss:**\n\n"
            "🥇 **Ranked by health score:**\n\n"
            "1. **Moong Dal Chilla** (GI 28, 138 kcal, 8.4g protein)\n"
            "   → Highest protein/calorie ratio, keeps you full 4+ hours\n\n"
            "2. **Besan Chilla** (GI 30, 148 kcal, 7.8g protein)\n"
            "   → Diabetic-friendly, rich in iron and zinc\n\n"
            "3. **Pesarattu** (GI 38, 148 kcal, 7.2g protein)\n"
            "   → Andhra green moong crepe — excellent for weight loss\n\n"
            "4. **Daliya Porridge** (GI 41, 102 kcal, 3.8g protein)\n"
            "   → Lowest calories, high fibre, sustained energy\n\n"
            "5. **Idli + Sambar** (GI 54, 116 kcal, 5.2g protein)\n"
            "   → Probiotic, low fat, traditional and satisfying\n\n"
            "❌ **Avoid for weight loss:** Aloo paratha (342 kcal), Sabudana khichdi (198 kcal, high GI), Puri-sabzi (328 kcal)"
        )
    elif "pcos" in q:
        return (
            "**Indian Diet for PCOS:**\n\n"
            "PCOS is driven by insulin resistance and inflammation. Diet fixes both.\n\n"
            "✅ **Best foods:**\n"
            "• Methi seeds: soak 1 tsp overnight, eat morning on empty stomach (reduces androgens)\n"
            "• Flaxseeds: 1 tbsp daily in curd — best hormone balancer\n"
            "• Rajma, chole, moong dal: low GI, high fibre, controls insulin\n"
            "• Green leafy vegetables daily: spinach, methi, moringa\n"
            "• Walnuts: 4-5 daily (omega-3 reduces testosterone)\n"
            "• Cinnamon: 1/2 tsp daily in warm water (improves insulin sensitivity)\n\n"
            "❌ **Avoid:**\n"
            "• Sugar, refined carbs, white rice in excess\n"
            "• Soy products (excess phytoestrogens can worsen PCOS)\n"
            "• Dairy excess (may increase IGF-1) — limit to 1-2 servings\n\n"
            "🏃 **Exercise:**\n"
            "• 30 min cardio + 20 min yoga daily — reduces androgen by 15-20%\n"
            "• Yoga: Baddha Konasana, Supta Baddha Konasana, Bhujangasana — specifically beneficial for PCOS"
        )
    else:
        return (
            "**Personalised Answer for " + profile["name"] + " (Goal: " + goal + "):**\n\n"
            "Based on your profile:\n"
            "• Daily calorie target: " + str(targets["kcal"]) + " kcal\n"
            "• Protein target: " + str(targets["prot"]) + "g\n"
            "• BMI: " + str(targets["bmi"]) + " (" + targets["bmi_cat"] + ")\n\n"
            "**General Indian Diet Recommendations:**\n"
            "• Follow a traditional Indian thali: dal + roti/rice + sabzi + curd + salad\n"
            "• Include at least 1 fermented food daily (curd, idli, dosa)\n"
            "• Eat seasonal and local produce — more nutritious and affordable\n"
            "• Cook in mustard oil, coconut oil or ghee — avoid refined vegetable oils\n"
            "• Use iron kadhai (improves iron content of food by 20%)\n\n"
            "For more specific advice, try one of the quick questions above or enter an Anthropic API key for AI-powered personalised guidance."
        )

# Patch the missing function name used in tab7
generate_rule_based_answer = _rule_answer

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — NUTRIENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab8:
    st.markdown(
        '<div class="eyebrow">Micronutrient Intelligence</div>'
        '<div class="h1">Nutrient Analysis 🔬</div>'
        '<p style="color:var(--muted);margin:8px 0 20px">ICMR Indian RDAs — benchmarked to Indian population needs.</p>',
        unsafe_allow_html=True
    )
    nc1,nc2,nc3,nc4 = st.columns(4)
    nc1.metric("Protein Target",  f"{targets['prot']}g",  f"{round(targets['prot']*4)} kcal")
    nc2.metric("Carbs Target",    f"{targets['carbs']}g", f"{round(targets['carbs']*4)} kcal")
    nc3.metric("Fat Target",      f"{targets['fat']}g",   f"{round(targets['fat']*9)} kcal")
    nc4.metric("Fibre Target",    "30–40g",               "ICMR RDA")
    st.divider()
    st.markdown("#### Micronutrient Panel")
    with st.expander("📝 Enter your estimated daily intake"):
        ni1,ni2,ni3 = st.columns(3)
        iron_got   = ni1.number_input("Iron (mg)",     0.0,50.0,  8.0,  0.5, key="iron_input")
        b12_got    = ni2.number_input("Vit B12 (mcg)", 0.0,10.0,  0.4 if diet=="Vegetarian" else 2.0, 0.1, key="b12_input")
        vitd_got   = ni3.number_input("Vit D (IU)",    0.0,2000.0,120.0,10.0, key="vitd_input")
        cal_got    = ni1.number_input("Calcium (mg)",  0.0,2000.0,500.0,50.0, key="cal_input")
        zinc_got   = ni2.number_input("Zinc (mg)",     0.0,30.0,  7.0,  0.5, key="zinc_input")
        folate_got = ni3.number_input("Folate (mcg)",  0.0,500.0, 100.0,10.0, key="folate_input")
    intake_vals = {"Iron":iron_got,"Vitamin B12":b12_got,"Vitamin D":vitd_got,"Calcium":cal_got,"Zinc":zinc_got,"Folate":folate_got}

    for nutrient, info in ICMR_RDA.items():
        rda    = info["female"] if gender=="Female" else info["male"]
        got    = intake_vals.get(nutrient, 0)
        pct    = round(got / rda * 100, 1) if rda > 0 else 0
        status = "deficient" if pct < 50 else "low" if pct < 75 else "ok"
        if nutrient == "Vitamin B12" and diet == "Vegetarian" and status == "ok": status = "low"
        icon, tip, foods = MICRO_TIPS.get(nutrient, ("💊","","[]"))
        cm = {"deficient":"#FF4B6E","low":"#F5A623","ok":"#4ECBA0"}
        lm = {"deficient":"🔴 Deficient","low":"🟡 Low","ok":"✅ Adequate"}
        bg = {"deficient":"rgba(255,75,110,.06)","low":"rgba(245,166,35,.06)","ok":"rgba(78,203,160,.06)"}
        bd = {"deficient":"rgba(255,75,110,.25)","low":"rgba(245,166,35,.25)","ok":"rgba(78,203,160,.2)"}
        st.markdown(
            '<div style="background:' + bg[status] + ';border:1px solid ' + bd[status] + ';border-radius:12px;padding:16px;margin-bottom:10px">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
            '<div style="font-weight:600;font-size:15px">' + icon + " " + nutrient + '</div>'
            '<span style="font-family:Space Mono,monospace;font-size:9px;padding:3px 10px;border-radius:10px;background:rgba(255,255,255,.06);color:' + cm[status] + '">' + lm[status] + '</span>'
            '</div>'
            '<div style="height:5px;background:rgba(255,255,255,.06);border-radius:3px;margin-bottom:10px;overflow:hidden">'
            '<div style="height:100%;width:' + str(min(100,pct)) + '%;background:' + cm[status] + ';border-radius:3px"></div>'
            '</div>'
            '<div style="font-size:12px;color:var(--muted);margin-bottom:6px">' + str(got) + " / " + str(rda) + " " + info["unit"] + " — " + str(pct) + "% of ICMR RDA</div>"
            '<div style="font-size:12px;color:rgba(255,248,240,.5)">💡 ' + tip + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        with st.expander(f"🍽️ Best Indian sources of {nutrient}"):
            for fi in foods: st.write(f"• {fi}")

    st.divider()
    import pandas as pd
    st.markdown("#### Glycemic Index Reference")
    gi_df = pd.DataFrame({
        "Food":["White Rice","Brown Rice","Basmati Rice","Roti","Bajra Roti","Dal","Rajma","Idli","Dosa","Potato","Ragi","Jowar","Sprouted Moong","Besan Chilla","Khichdi"],
        "GI":[72,50,56,62,54,29,29,77,55,80,68,50,25,30,55],
        "Category":["High","Medium","Medium","Medium","Medium","Low","Low","High","Medium","High","Medium","Medium","Low","Low","Medium"],
        "Kcal/100g":[130,123,121,297,278,116,143,58,168,77,328,264,62,148,135],
        "Best for":["General use","Diabetic","Biryani","Daily","Diabetes/PCOS","All goals","Weight loss","Breakfast","Breakfast","Energy","Calcium","Diabetic","Protein boost","Weight loss","Sick/recover"],
    })
    st.dataframe(gi_df, use_container_width=True, hide_index=True)

    if conditions:
        st.divider()
        st.markdown("#### Medical Condition Guidance")
        cond_tips = {
            "Diabetes":    ("🩸","Low-GI diet. Bajra roti, brown rice, dal, leafy veg. Avoid maida, white rice, sugar. Small meals every 3 hrs. Walk 10 min after meals."),
            "Hypertension":("❤️","Limit sodium <2g/day. No pickles, papads, packaged food. Eat potassium-rich: banana, coconut water, spinach. DASH diet principles."),
            "Anaemia":     ("🩸","Iron-rich: palak, rajma, horse gram, dates, til. Pair with Vitamin C. Avoid tea/coffee 1hr after meals. Cook in iron kadhai."),
            "PCOS":        ("🌸","Low-GI, anti-inflammatory diet. Methi seeds daily. Omega-3 (fish/walnuts/flaxseeds). Limit sugar and refined carbs. Daily yoga + cardio."),
            "Thyroid":     ("🦋","Cook cruciferous veg before eating. Iodised salt. Selenium: sunflower seeds. Take medication 30-60 min before eating."),
        }
        for c in conditions:
            if c in cond_tips:
                icon2, text = cond_tips[c]
                st.markdown(alert("info", icon2 + " **" + c + ":** " + text), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab9:
    st.markdown('<div class="eyebrow">Your Journey</div><div class="h1">Progress & Achievements 📊</div>', unsafe_allow_html=True)
    st.markdown("")
    pg1, pg2 = st.columns(2)
    with pg1:
        st.markdown("#### BMI & 7-Day Calories")
        st.markdown("**BMI** — " + str(targets["bmi"]) + " (" + targets["bmi_cat"] + ")")
        import pandas as pd
        chart_rows = []
        for i in range(6,-1,-1):
            d   = (today - datetime.timedelta(days=i)).isoformat()
            lg  = st.session_state["meal_log"].get(d,{})
            kd  = sum(float(dish.get("kcal",0) or 0) for dishes in lg.values() for dish in dishes)
            chart_rows.append({"date":(today-datetime.timedelta(days=i)).strftime("%a %d"),"Calories":round(kd),"Target":targets["kcal"]})
        cdf = pd.DataFrame(chart_rows)
        st.bar_chart(cdf.set_index("date")[["Calories","Target"]], color=["#FF6B2B","#4ECBA0"])

        st.divider()
        st.markdown("#### 👤 Profile Summary")
        for k,v in [("Name",profile["name"]),("Gender",gender),("Age",f"{age} yrs"),("Weight",f"{weight} kg"),("Height",f"{height} cm"),("BMR",f"{targets['bmr']} kcal"),("TDEE",f"{targets['tdee']} kcal"),("Goal",goal),("Diet",diet)]:
            c1,c2 = st.columns([2,3])
            c1.caption(k); c2.write(f"**{v}**")

    with pg2:
        meals_tot  = sum(len(d) for lg in st.session_state["meal_log"].values() for d in lg.values())
        days_logged = len([d for d,lg in st.session_state["meal_log"].items() if any(lg.values())])
        streak = 0
        for i in range(30):
            d  = (today - datetime.timedelta(days=i)).isoformat()
            lg = st.session_state["meal_log"].get(d,{})
            if any(lg.values()): streak += 1
            else: break

        st.markdown("#### 🏆 Achievements")
        achievements = [
            ("🌱","First Step",    "Profile created",            True),
            ("📝","First Log",     "Log your first meal",         meals_tot>=1),
            ("🔥","3-Day Streak",  "3 days in a row",             streak>=3),
            ("💪","Protein Pro",   "Hit protein 7 days",          False),
            ("🥦","Veggie Champ",  "7 veg days",                  diet=="Vegetarian"),
            ("⚖️","BMI Target",    "Healthy BMI",                 18.5<=targets["bmi"]<=24.9),
            ("⭐","Wellness Star", "Score > 80",                  targets["wellness"]>=80),
            ("📅","Week Planner",  "Plan full week",              len(st.session_state["weekly_plan"])>=7),
            ("🛒","Smart Shopper", "Generate shopping list",      len(st.session_state["shopping_list"])>0),
            ("💧","Hydrated",      f"{round(targets['water']/250)} glasses/day", st.session_state["water_glasses"]>=round(targets["water"]/250)),
            ("🤖","AI User",       "Use AI Health Advisor",       len(st.session_state["ai_chat"])>0),
            ("🏆","Champion",      "30-day streak",               streak>=30),
        ]
        ac = st.columns(4)
        for i,(icon,title,desc,unlocked) in enumerate(achievements):
            with ac[i%4]:
                bg  = "rgba(255,107,43,.08)" if unlocked else "rgba(255,255,255,.02)"
                bdr = "rgba(255,107,43,.3)"  if unlocked else "rgba(255,255,255,.07)"
                flt = "none" if unlocked else "grayscale(1) opacity(.35)"
                st.markdown(
                    '<div style="background:' + bg + ';border:1px solid ' + bdr + ';border-radius:12px;padding:14px;text-align:center;margin-bottom:10px;min-height:100px">'
                    '<div style="font-size:26px;filter:' + flt + ';margin-bottom:6px">' + icon + '</div>'
                    '<div style="font-size:11px;font-weight:600;line-height:1.3">' + title + '</div>'
                    '<div style="font-size:9px;color:var(--muted);margin-top:3px">' + desc + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

        st.divider()
        st.markdown("#### ⭐ Wellness Score")
        bs = 40 if 18.5<=targets["bmi"]<=24.9 else (28 if 17<=targets["bmi"]<30 else 15)
        ls = min(20, days_logged*3)
        ss = min(20, streak*2)
        hs2 = min(10, st.session_state["water_glasses"])
        tw  = bs + ls + ss + hs2
        hc  = "#4ECBA0" if tw>=70 else "#F5A623" if tw>=50 else "#FF4B6E"
        st.markdown(
            '<div style="text-align:center;margin-bottom:16px">'
            '<div class="health-score" style="color:' + hc + '">' + str(tw) + '</div>'
            '<div style="font-size:12px;color:var(--muted)">Wellness Score / 90</div>'
            '</div>',
            unsafe_allow_html=True
        )
        for label,got,total in [("BMI Score",bs,40),("Logging Habit",ls,20),("Streak Bonus",ss,20),("Hydration",hs2,10)]:
            st.markdown(f"**{label}** — {got}/{total}")
            st.progress(float(got)/float(total) if total else 0.0)

        st.divider()
        ms1,ms2,ms3 = st.columns(3)
        ms1.metric("Total Meals",meals_tot)
        ms2.metric("Days Tracked",days_logged)
        ms3.metric("Streak",f"{streak} days","🔥" if streak>0 else "")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    '<div style="text-align:center;padding:20px 0">'
    '<div style="font-family:Playfair Display,serif;font-size:20px;font-weight:700;color:#FF6B2B;margin-bottom:6px">🥗 Nourish</div>'
    '<div style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:.25em;color:rgba(255,248,240,.2);text-transform:uppercase">'
    'Indian Diet Planner v4.0 · AI Health Advisor · Exercise Planner · Meal Logger · Weekly Planner · ICMR-Benchmarked'
    '</div></div>',
    unsafe_allow_html=True
)
