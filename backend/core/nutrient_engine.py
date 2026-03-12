"""
Nourish — Nutrient Assistance Engine (Priority ②)

The heart of the "extraordinary" promise:
- Mifflin-St Jeor BMR/TDEE
- Macro targets by goal
- Micronutrient deficiency detection (ICMR RDA)
- Iron, B12, Vitamin D, Calcium, Zinc, Folate alerts
- Wellness Score synthesis
- Auto-rebalance suggestions
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import math

# ── ICMR RDA (Indian Council of Medical Research) ─────────────────────────────
ICMR_RDA = {
    "protein_g":      {"male": 60,    "female": 55,   "unit": "g",   "label": "Protein"},
    "carbs_g":        {"male": 300,   "female": 230,  "unit": "g",   "label": "Carbohydrates"},
    "fat_g":          {"male": 60,    "female": 50,   "unit": "g",   "label": "Fat"},
    "fiber_g":        {"male": 40,    "female": 35,   "unit": "g",   "label": "Dietary Fibre"},
    "iron_mg":        {"male": 17,    "female": 21,   "unit": "mg",  "label": "Iron"},
    "calcium_mg":     {"male": 1000,  "female": 1000, "unit": "mg",  "label": "Calcium"},
    "b12_mcg":        {"male": 2.2,   "female": 2.2,  "unit": "mcg", "label": "Vitamin B12"},
    "vitamin_d_iu":   {"male": 600,   "female": 600,  "unit": "IU",  "label": "Vitamin D"},
    "zinc_mg":        {"male": 12,    "female": 10,   "unit": "mg",  "label": "Zinc"},
    "folate_mcg":     {"male": 200,   "female": 200,  "unit": "mcg", "label": "Folate"},
    "sodium_mg":      {"male": 2000,  "female": 2000, "unit": "mg",  "label": "Sodium"},
}

ACTIVITY_FACTORS = {
    "sedentary":   1.2,   # desk job, little exercise
    "light":       1.375, # light exercise 1-3 days/week
    "moderate":    1.55,  # moderate exercise 3-5 days/week
    "active":      1.725, # hard exercise 6-7 days/week
}

GOAL_CALORIE_DELTA = {
    "lose_weight":      -500,
    "lose_weight_fast": -750,
    "maintain":          0,
    "gain_weight":      +300,
    "gain_muscle":      +200,
}

GOAL_MACRO_SPLITS = {
    # (protein%, carbs%, fat%)
    "lose_weight":      (0.35, 0.40, 0.25),
    "lose_weight_fast": (0.40, 0.35, 0.25),
    "maintain":         (0.25, 0.50, 0.25),
    "gain_weight":      (0.25, 0.50, 0.25),
    "gain_muscle":      (0.35, 0.45, 0.20),
}

BMI_CATEGORIES = {
    (0,   18.5): ("Underweight", "#00D4FF"),
    (18.5, 25.0): ("Healthy Weight", "#4ECBA0"),
    (25.0, 30.0): ("Overweight", "#F5A623"),
    (30.0, 35.0): ("Obese Class I", "#FF6B2B"),
    (35.0, 100):  ("Obese Class II+", "#FF4B6E"),
}

# Micronutrients Indians are commonly deficient in, with Indian food remedies
MICRO_DEFICIENCY_REMEDIES = {
    "iron": {
        "label": "Iron",
        "unit": "mg",
        "common_in": "vegetarians, women, elderly",
        "symptoms": "Fatigue, breathlessness, pale skin, brittle nails",
        "foods": [
            "Spinach (palak) dal — high iron + vitamin C for absorption",
            "Iron-fortified atta (whole wheat flour)",
            "Rajma with amla chutney",
            "Sesame (til) ladoo",
            "Dried figs (anjeer) and dates",
            "Horse gram (kulthi) dal",
        ],
        "tip": "Pair iron-rich foods with Vitamin C (lemon, amla) and avoid tea/coffee 30 min after meals.",
    },
    "b12": {
        "label": "Vitamin B12",
        "unit": "mcg",
        "common_in": "strict vegetarians, vegans",
        "symptoms": "Fatigue, neurological symptoms, memory issues, anaemia",
        "foods": [
            "Fortified milk or plant milk",
            "Curd (yogurt) — contains small amounts",
            "Paneer from fortified milk",
            "Idli/dosa fermented batter",
            "B12 supplementation strongly recommended for pure vegetarians",
        ],
        "tip": "B12 is nearly absent in plant foods. If vegetarian, consider a supplement.",
    },
    "vitamin_d": {
        "label": "Vitamin D",
        "unit": "IU",
        "common_in": "urban Indians with limited sun exposure",
        "symptoms": "Bone pain, muscle weakness, fatigue, frequent infections",
        "foods": [
            "15–20 minutes morning sunlight (before 10am)",
            "Fortified milk and dairy",
            "Egg yolk (if non-veg)",
            "Mushrooms exposed to sunlight",
            "Fatty fish like surmai/mackerel (if non-veg)",
        ],
        "tip": "Most Indians are deficient. Sunlight is the best source — aim for 15 min/day on arms and face.",
    },
    "calcium": {
        "label": "Calcium",
        "unit": "mg",
        "common_in": "post-menopausal women, adolescents",
        "symptoms": "Weak bones, muscle cramps, dental issues",
        "foods": [
            "Ragi (finger millet) — highest calcium among cereals",
            "Sesame seeds (til) — sprinkle on dal or sabzi",
            "Curd (yogurt) and chaas (buttermilk)",
            "Paneer and milk",
            "Amaranth (rajgira) ladoo",
            "Dried figs and almonds",
        ],
        "tip": "Avoid excess oxalates (raw spinach, beet) when combining with calcium foods — cooking reduces oxalates.",
    },
    "zinc": {
        "label": "Zinc",
        "unit": "mg",
        "common_in": "vegetarians (phytates reduce absorption)",
        "symptoms": "Poor wound healing, hair loss, taste/smell loss, frequent colds",
        "foods": [
            "Pumpkin seeds (kaddu beej) — top plant zinc source",
            "Whole wheat rotis",
            "Lentils (masoor, moong dal)",
            "Cashews and pine nuts",
            "Soak/sprout legumes to reduce phytates",
        ],
        "tip": "Soaking legumes overnight improves zinc absorption by reducing phytic acid.",
    },
    "folate": {
        "label": "Folate (B9)",
        "unit": "mcg",
        "common_in": "pregnant women, people with poor vegetable intake",
        "symptoms": "Megaloblastic anaemia, neural tube defects in pregnancy",
        "foods": [
            "Methi (fenugreek) leaves — highest folate vegetable",
            "Spinach (palak) cooked",
            "Moong sprouts",
            "Chana dal",
            "Drumstick (moringa) leaves",
            "Avocado and lentils",
        ],
        "tip": "Folate is heat-sensitive. Steam or lightly sauté greens to retain more.",
    },
}


@dataclass
class UserProfile:
    name:        str
    gender:      str   # "male" | "female"
    age:         int
    weight_kg:   float
    height_cm:   float
    activity:    str   # key from ACTIVITY_FACTORS
    goal:        str   # key from GOAL_CALORIE_DELTA
    diet:        str   # "vegetarian" | "non-vegetarian"
    medical:     list  = field(default_factory=list)  # ["diabetes","hypertension",...]
    region:      str   = "North"


@dataclass
class NutritionTargets:
    bmr:         float
    tdee:        float
    target_kcal: float
    protein_g:   float
    carbs_g:     float
    fat_g:       float
    bmi:         float
    bmi_category: str
    bmi_color:   str
    wellness_score: int
    water_ml:    float


@dataclass
class DeficiencyAlert:
    nutrient:    str
    label:       str
    status:      str   # "deficient" | "low" | "adequate"
    current_pct: float # % of RDA
    rda:         float
    unit:        str
    foods:       list
    tip:         str
    symptoms:    str
    priority:    int   # 1=critical, 2=moderate, 3=low


class NutrientEngine:
    """
    Priority ② — The Nutrient Assistance Engine.
    All nutrition science lives here.
    """

    def calculate(self, profile: UserProfile) -> NutritionTargets:
        bmr   = self._bmr(profile)
        tdee  = bmr * ACTIVITY_FACTORS.get(profile.activity, 1.375)
        delta = GOAL_CALORIE_DELTA.get(profile.goal, 0)
        target_kcal = max(1200, round(tdee + delta))

        splits = GOAL_MACRO_SPLITS.get(profile.goal, (0.25, 0.50, 0.25))
        p_pct, c_pct, f_pct = splits

        protein_g = round(target_kcal * p_pct / 4, 1)
        carbs_g   = round(target_kcal * c_pct / 4, 1)
        fat_g     = round(target_kcal * f_pct / 9, 1)

        bmi           = self._bmi(profile)
        cat, color    = self._bmi_category(bmi)
        wellness      = self._wellness_score(profile, bmi)
        water_ml      = self._water_target(profile)

        return NutritionTargets(
            bmr=round(bmr),
            tdee=round(tdee),
            target_kcal=target_kcal,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            bmi=round(bmi, 1),
            bmi_category=cat,
            bmi_color=color,
            wellness_score=wellness,
            water_ml=water_ml,
        )

    def analyse_deficiencies(
        self,
        profile: UserProfile,
        intake: dict,           # {"iron_mg": 8, "b12_mcg": 0.5, ...}
    ) -> list[DeficiencyAlert]:
        """
        Compare intake against ICMR RDA.
        Returns list of DeficiencyAlert sorted by priority.
        """
        gender  = profile.gender
        alerts  = []
        key_map = {
            "iron":      ("iron_mg",      MICRO_DEFICIENCY_REMEDIES["iron"]),
            "b12":       ("b12_mcg",      MICRO_DEFICIENCY_REMEDIES["b12"]),
            "vitamin_d": ("vitamin_d_iu", MICRO_DEFICIENCY_REMEDIES["vitamin_d"]),
            "calcium":   ("calcium_mg",   MICRO_DEFICIENCY_REMEDIES["calcium"]),
            "zinc":      ("zinc_mg",      MICRO_DEFICIENCY_REMEDIES["zinc"]),
            "folate":    ("folate_mcg",   MICRO_DEFICIENCY_REMEDIES["folate"]),
        }

        for key, (rda_key, remedy) in key_map.items():
            if rda_key not in ICMR_RDA:
                continue
            rda    = ICMR_RDA[rda_key].get(gender, ICMR_RDA[rda_key]["male"])
            unit   = ICMR_RDA[rda_key]["unit"]
            got    = intake.get(rda_key, 0) or 0
            pct    = round(got / rda * 100, 1) if rda else 0

            if pct < 50:
                status   = "deficient"
                priority = 1
            elif pct < 75:
                status   = "low"
                priority = 2
            else:
                status   = "adequate"
                priority = 3

            alerts.append(DeficiencyAlert(
                nutrient=key,
                label=remedy["label"],
                status=status,
                current_pct=pct,
                rda=rda,
                unit=unit,
                foods=remedy["foods"],
                tip=remedy["tip"],
                symptoms=remedy["symptoms"],
                priority=priority,
            ))

        # Extra alert for vegetarians: flag B12 as critical always
        if profile.diet == "vegetarian":
            for a in alerts:
                if a.nutrient == "b12":
                    a.priority = 1
                    if a.status == "adequate":
                        a.status = "low"
                    break

        return sorted(alerts, key=lambda x: x.priority)

    def meal_split(self, profile: UserProfile, targets: NutritionTargets) -> list[dict]:
        """
        Distribute daily calories across meals based on BMI category.
        Underweight → 5 meals, Normal/Overweight → 4 meals, Obese → 3 meals.
        """
        bmi = targets.bmi

        if bmi < 18.5:
            meals = [
                {"name": "Breakfast",     "time": "8:00 AM",  "pct": 0.25},
                {"name": "Mid-Morning",   "time": "10:30 AM", "pct": 0.10},
                {"name": "Lunch",         "time": "1:00 PM",  "pct": 0.30},
                {"name": "Evening Snack", "time": "4:30 PM",  "pct": 0.10},
                {"name": "Dinner",        "time": "7:30 PM",  "pct": 0.25},
            ]
        elif bmi < 30:
            meals = [
                {"name": "Breakfast",     "time": "8:00 AM",  "pct": 0.25},
                {"name": "Lunch",         "time": "1:00 PM",  "pct": 0.35},
                {"name": "Evening Snack", "time": "4:30 PM",  "pct": 0.10},
                {"name": "Dinner",        "time": "7:30 PM",  "pct": 0.30},
            ]
        else:
            meals = [
                {"name": "Breakfast", "time": "8:30 AM",  "pct": 0.28},
                {"name": "Lunch",     "time": "1:00 PM",  "pct": 0.38},
                {"name": "Dinner",    "time": "7:00 PM",  "pct": 0.34},
            ]

        total = targets.target_kcal
        for m in meals:
            m["target_kcal"] = round(total * m["pct"])
            m["target_protein_g"] = round(targets.protein_g * m["pct"], 1)
            m["target_carbs_g"]   = round(targets.carbs_g   * m["pct"], 1)
            m["target_fat_g"]     = round(targets.fat_g     * m["pct"], 1)

        return meals

    def wellness_score(
        self,
        profile: UserProfile,
        targets: NutritionTargets,
        intake_today: dict,
        streak_days: int = 0,
    ) -> dict:
        """
        Single synthesized Wellness Score (0–100).
        Combines BMI, macro adherence, micronutrient status, streak.
        """
        bmi    = targets.bmi
        scores = {}

        # BMI sub-score (40 points)
        if 18.5 <= bmi <= 24.9:
            scores["bmi"] = 40
        elif 17.5 <= bmi < 18.5 or 25.0 <= bmi < 27.5:
            scores["bmi"] = 32
        elif 15.0 <= bmi < 17.5 or 27.5 <= bmi < 30.0:
            scores["bmi"] = 22
        else:
            scores["bmi"] = 12

        # Macro adherence sub-score (30 points)
        macro_score = 0
        for nutrient, target_attr in [
            ("protein_g", "protein_g"),
            ("carbs_g",   "carbs_g"),
            ("fat_g",     "fat_g"),
        ]:
            got    = intake_today.get(nutrient, 0) or 0
            target = getattr(targets, target_attr)
            if target > 0:
                ratio = got / target
                macro_score += 10 * min(1.0, ratio)

        scores["macros"] = round(macro_score)

        # Streak bonus (up to 20 points)
        streak_bonus = min(20, streak_days * 2)
        scores["streak"] = streak_bonus

        # Hydration (10 points)
        water_got    = intake_today.get("water_ml", 0) or 0
        water_target = targets.water_ml
        scores["hydration"] = round(10 * min(1.0, water_got / water_target)) if water_target else 5

        total = sum(scores.values())

        grade_map = [
            (90, "Excellent", "#4ECBA0"),
            (75, "Good",      "#F5A623"),
            (55, "Fair",      "#FF6B2B"),
            (0,  "Needs Work","#FF4B6E"),
        ]
        grade, color = next((g, c) for threshold, g, c in grade_map if total >= threshold)

        return {
            "total":      total,
            "grade":      grade,
            "color":      color,
            "breakdown":  scores,
        }

    def medical_filters(self, medical_conditions: list) -> dict:
        """Return food filtering rules for medical conditions."""
        rules = {}
        for cond in medical_conditions:
            c = cond.lower()
            if "diabet" in c:
                rules["max_gi"]      = 55
                rules["low_sugar"]   = True
                rules["note"]        = "Low GI foods only (GI < 55). Prefer bajra, jowar, whole grains."
            if "hypertens" in c or "blood pressure" in c:
                rules["max_salt_g"]  = 1.5
                rules["low_sodium"]  = True
                rules["note"]        = "Limit salt to 1.5g/100g. Avoid papads, pickles, packaged snacks."
            if "anaemi" in c or "anemia" in c:
                rules["high_iron"]   = True
                rules["note"]        = "Prioritise iron-rich foods. Pair with Vitamin C. Avoid calcium with iron meals."
            if "pcos" in c:
                rules["max_gi"]      = 50
                rules["high_fiber"]  = True
                rules["note"]        = "Low GI + high fibre diet supports PCOS management."
            if "thyroid" in c:
                rules["avoid_raw_cruciferous"] = True
                rules["note"]        = "Avoid raw cauliflower, cabbage, broccoli. Cook thoroughly."
        return rules

    # ── Private helpers ───────────────────────────────────────────────────────

    def _bmr(self, p: UserProfile) -> float:
        """Mifflin-St Jeor BMR formula."""
        base = 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age
        return base + 5 if p.gender == "male" else base - 161

    def _bmi(self, p: UserProfile) -> float:
        h_m = p.height_cm / 100
        return p.weight_kg / (h_m ** 2)

    def _bmi_category(self, bmi: float) -> tuple[str, str]:
        for (lo, hi), (label, color) in BMI_CATEGORIES.items():
            if lo <= bmi < hi:
                return label, color
        return "Unknown", "#888"

    def _wellness_score(self, p: UserProfile, bmi: float) -> int:
        """Quick wellness score for initial display (without intake data)."""
        base = 70
        if 18.5 <= bmi <= 24.9:
            base += 15
        elif 25.0 <= bmi < 30.0:
            base -= 5
        elif bmi >= 30:
            base -= 15
        elif bmi < 18.5:
            base -= 10
        if p.diet == "vegetarian":
            base += 3
        return max(30, min(100, base))

    def _water_target(self, p: UserProfile) -> float:
        """Daily water target in ml. Adjusted for Indian climate."""
        base_ml = p.weight_kg * 35  # 35ml/kg
        if p.activity in ("active",):
            base_ml += 500
        elif p.activity == "moderate":
            base_ml += 250
        # India climate adjustment: +200ml for warm/humid
        base_ml += 200
        return round(base_ml)
