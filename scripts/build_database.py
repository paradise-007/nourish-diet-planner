"""
Nourish - Data Architecture Pipeline (Priority ①)
Merges indian_food.csv + Indian_Food_DF.csv into a clean, validated JSON database.

Run:  python scripts/build_database.py
Output: backend/data/nourish_foods.json
"""

import csv
import json
import re
import os
import hashlib
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
FOOD_CSV = DATA_DIR / "indian_food.csv"
NUTRI_CSV = DATA_DIR / "Indian_Food_DF.csv"
OUT_JSON  = DATA_DIR / "nourish_foods.json"
CHANGELOG = DATA_DIR / "database_changelog.json"

# ── ICMR RDA Reference (per day, adults 19-50) ───────────────────────────────
ICMR_RDA = {
    "protein_g":    60,    # grams
    "carbs_g":     300,    # grams
    "fat_g":        60,    # grams
    "fiber_g":      40,    # grams
    "iron_mg":      17,    # mg
    "calcium_mg": 1000,    # mg
    "b12_mcg":       2.2,  # mcg
    "vitamin_d_iu": 600,   # IU
    "zinc_mg":      12,    # mg
    "folate_mcg":  200,    # mcg
    "sodium_mg":  2000,    # mg
}

# ── Glycemic Index table for common Indian dishes (evidence-based estimates) ──
GI_TABLE = {
    "white rice": 72, "brown rice": 50, "idli": 77, "dosa": 55,
    "roti": 62, "chapati": 52, "naan": 71, "paratha": 66,
    "poha": 55, "upma": 50, "dal": 29, "rajma": 29,
    "chana": 28, "moong": 25, "sambar": 30, "rasam": 35,
    "khichdi": 55, "biryani": 65, "pulao": 68, "puri": 62,
    "bhatura": 68, "halwa": 80, "kheer": 75, "ladoo": 78,
    "gulab jamun": 76, "barfi": 72, "jalebi": 82, "payasam": 72,
    "bread": 70, "poori": 62, "pav": 68, "dhokla": 35,
    "khandvi": 38, "thepla": 48, "kadhi": 40, "sabzi": 45,
    "paneer": 27, "curd": 36, "lassi": 40, "buttermilk": 35,
    "mango": 51, "banana": 51, "apple": 36, "papaya": 60,
    "potato": 80, "sweet potato": 63, "yam": 54, "tapioca": 70,
}

# ── Ayurvedic Dosha mapping by flavor_profile ─────────────────────────────────
DOSHA_MAP = {
    "sweet":   {"vata": "balances", "pitta": "balances", "kapha": "aggravates"},
    "spicy":   {"vata": "aggravates","pitta": "aggravates","kapha": "balances"},
    "sour":    {"vata": "balances", "pitta": "aggravates","kapha": "aggravates"},
    "bitter":  {"vata": "aggravates","pitta": "balances", "kapha": "balances"},
    "salty":   {"vata": "balances", "pitta": "aggravates","kapha": "aggravates"},
    "mild":    {"vata": "balances", "pitta": "balances", "kapha": "neutral"},
    "umami":   {"vata": "balances", "pitta": "neutral",  "kapha": "neutral"},
}

# ── Non-veg keywords ──────────────────────────────────────────────────────────
NONVEG_KEYWORDS = {
    "chicken", "mutton", "lamb", "beef", "pork", "fish", "prawn", "shrimp",
    "crab", "lobster", "egg", "meat", "keema", "kheema", "mince", "duck",
    "quail", "turkey", "tuna", "salmon", "mackerel", "sardine", "hilsa",
    "rohu", "catfish", "crayfish", "oyster", "squid", "octopus",
}


def parse_energy(raw: str):
    """Parse mixed kJ/kcal strings like '1,117 kj\\n(267 kcal)' → (kj, kcal)."""
    if not raw or not isinstance(raw, str):
        return None, None

    raw = raw.replace(",", "").lower()
    kj_match   = re.search(r"([\d.]+)\s*kj",   raw)
    kcal_match = re.search(r"([\d.]+)\s*kcal", raw)

    kj   = float(kj_match.group(1))   if kj_match   else None
    kcal = float(kcal_match.group(1)) if kcal_match else None

    # Derive missing value
    if kj and not kcal:
        kcal = round(kj / 4.184, 1)
    if kcal and not kj:
        kj = round(kcal * 4.184, 1)

    return kj, kcal


def parse_g(val: str):
    """Parse '14.8 g' → 14.8."""
    if not val or not isinstance(val, str):
        return None
    m = re.search(r"([\d.]+)", val)
    return float(m.group(1)) if m else None


def get_gi(name: str):
    """Estimate GI for a dish by checking known keywords."""
    name_lower = name.lower()
    for key, gi in GI_TABLE.items():
        if key in name_lower:
            return gi
    return None


def get_gl(gi, carbs_g, serving_g=150):
    """Glycemic Load = GI × carbs_per_serving / 100."""
    if gi is None or carbs_g is None:
        return None
    carbs_serving = carbs_g * (serving_g / 100)
    return round(gi * carbs_serving / 100, 1)


def confidence_score(item: dict) -> float:
    """Data confidence score 0–1 based on populated nutrient fields."""
    fields = ["kj", "kcal", "protein_g", "carbs_g", "fat_g", "fiber_g"]
    filled = sum(1 for f in fields if item.get(f) is not None)
    return round(filled / len(fields), 2)


def validate_macros(item: dict):
    """Check if protein+carb+fat calories are within 20% of total kcal."""
    p = item.get("protein_g") or 0
    c = item.get("carbs_g")   or 0
    f = item.get("fat_g")     or 0
    kcal = item.get("kcal")

    if not kcal or kcal <= 0:
        return None

    calc = (p * 4) + (c * 4) + (f * 9)
    if calc == 0:
        return None

    ratio = calc / kcal
    return "valid" if 0.7 <= ratio <= 1.3 else "suspect"


def detect_diet(name: str, ingredients: str, declared: str) -> str:
    """Detect veg/non-veg from ingredients and name."""
    text = f"{name} {ingredients}".lower()
    for kw in NONVEG_KEYWORDS:
        if kw in text:
            return "non-vegetarian"
    return declared or "vegetarian"


def get_dosha(flavor: str) -> dict:
    """Get Ayurvedic dosha influence for flavor profile."""
    return DOSHA_MAP.get((flavor or "").lower(), {})


def dish_id(name: str) -> str:
    """Stable short ID from dish name."""
    return hashlib.md5(name.lower().encode()).hexdigest()[:8]


def load_indian_food_csv() -> dict:
    """Load indian_food.csv → dict keyed by normalised name."""
    dishes = {}
    with open(FOOD_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            key  = name.lower()
            dishes[key] = {
                "id":           dish_id(name),
                "name":         name,
                "ingredients":  row.get("ingredients", "").strip(),
                "diet":         detect_diet(name, row.get("ingredients",""), row.get("diet","")),
                "prep_min":     int(row["prep_time"]) if row.get("prep_time","").strip().isdigit() else None,
                "cook_min":     int(row["cook_time"]) if row.get("cook_time","").strip().isdigit() else None,
                "flavor":       row.get("flavor_profile","").strip(),
                "course":       row.get("course","").strip(),
                "state":        row.get("state","").strip(),
                "region":       row.get("region","").strip(),
                "dosha":        get_dosha(row.get("flavor_profile","")),
                # nutrients filled later from nutritional CSV
                "kj":          None,
                "kcal":        None,
                "protein_g":   None,
                "carbs_g":     None,
                "fat_g":       None,
                "fiber_g":     None,
                "sugar_g":     None,
                "salt_g":      None,
                "sat_fat_g":   None,
                "gi":          get_gi(name),
                "source":      "indian_food_csv",
            }
    return dishes


def load_nutri_csv(dishes: dict):
    """Merge nutritional data from Indian_Food_DF.csv into dishes dict."""
    matched = 0
    added   = 0

    with open(NUTRI_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name","").strip()
            if not name:
                continue

            kj, kcal = parse_energy(row.get("nutri_energy", ""))
            if not kj:
                continue  # skip rows with no energy data

            nutrients = {
                "kj":        kj,
                "kcal":      kcal,
                "protein_g": parse_g(row.get("nutri_protein","")),
                "carbs_g":   parse_g(row.get("nutri_carbohydrate","")),
                "fat_g":     parse_g(row.get("nutri_fat","")),
                "fiber_g":   parse_g(row.get("nutri_fiber","")),
                "sugar_g":   parse_g(row.get("nutri_sugar","")),
                "salt_g":    parse_g(row.get("nutri_salt","")),
                "sat_fat_g": parse_g(row.get("nutri_satuFat","")),
            }

            key = name.lower()
            if key in dishes:
                dishes[key].update(nutrients)
                dishes[key]["source"] = "merged"
                matched += 1
            else:
                # New dish from nutritional CSV
                diet = detect_diet(name, "", "")
                dishes[key] = {
                    "id":          dish_id(name),
                    "name":        name,
                    "ingredients": "",
                    "diet":        diet,
                    "prep_min":    None,
                    "cook_min":    None,
                    "flavor":      "",
                    "course":      "main course",
                    "state":       "",
                    "region":      "",
                    "dosha":       {},
                    "gi":          get_gi(name),
                    "source":      "nutri_csv",
                    **nutrients,
                }
                added += 1

    print(f"  Merged nutritional data: {matched} matched, {added} added from nutritional CSV")


def enrich_and_validate(dishes: dict) -> list:
    """Add confidence scores, GL, macro validation; filter unrealistic values."""
    result = []
    invalid = 0

    for key, item in dishes.items():
        # Skip entries with no energy data at all
        if item.get("kj") is None and item.get("kcal") is None:
            # Estimate kcal from macros if available
            p = item.get("protein_g") or 0
            c = item.get("carbs_g")   or 0
            f_g = item.get("fat_g")   or 0
            if p + c + f_g > 0:
                item["kcal"] = round((p * 4) + (c * 4) + (f_g * 9), 1)
                item["kj"]   = round(item["kcal"] * 4.184, 1)
            else:
                invalid += 1
                continue

        # Sanity filter: 20 kcal–2000 kcal per 100g
        kcal = item.get("kcal", 0) or 0
        if kcal < 20 or kcal > 2000:
            invalid += 1
            continue

        # Glycemic Load
        item["gl"] = get_gl(item.get("gi"), item.get("carbs_g"))

        # Macro validation
        item["macro_valid"] = validate_macros(item)

        # Confidence score
        item["confidence"] = confidence_score(item)

        # Nutrient % of ICMR RDA per 100g serving
        item["rda_pct"] = {}
        if item.get("protein_g"):
            item["rda_pct"]["protein"] = round(item["protein_g"] / ICMR_RDA["protein_g"] * 100, 1)
        if item.get("fiber_g"):
            item["rda_pct"]["fiber"]   = round(item["fiber_g"]   / ICMR_RDA["fiber_g"]   * 100, 1)

        result.append(item)

    print(f"  Filtered {invalid} invalid/incomplete entries")
    return result


def main():
    print("🥗 Nourish Database Builder — Priority ①: Data Architecture\n")
    print(f"  Loading indian_food.csv ({FOOD_CSV})...")
    dishes = load_indian_food_csv()
    print(f"  Loaded {len(dishes)} dishes from indian_food.csv")

    print(f"  Loading Indian_Food_DF.csv ({NUTRI_CSV})...")
    load_nutri_csv(dishes)
    print(f"  Total dishes after merge: {len(dishes)}")

    print("  Enriching, validating, scoring...")
    final = enrich_and_validate(dishes)
    print(f"  Final validated dishes: {len(final)}")

    # Stats
    veg    = sum(1 for d in final if "vegetarian" in d["diet"] and "non" not in d["diet"])
    nonveg = sum(1 for d in final if "non" in d["diet"])
    hi_conf = sum(1 for d in final if d["confidence"] >= 0.8)
    has_gi  = sum(1 for d in final if d.get("gi") is not None)

    print(f"\n  📊 Database Stats:")
    print(f"     Vegetarian  : {veg}")
    print(f"     Non-Veg     : {nonveg}")
    print(f"     High-conf.  : {hi_conf} (confidence ≥ 0.8)")
    print(f"     With GI data: {has_gi}")

    # Write output
    out = {
        "version":    "1.0.0",
        "built_at":   __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "total":      len(final),
        "icmr_rda":   ICMR_RDA,
        "foods":      final,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n  ✅ Written to {OUT_JSON}")

    # Write changelog entry
    changelog = []
    if CHANGELOG.exists():
        with open(CHANGELOG) as f:
            changelog = json.load(f)
    changelog.append({
        "version":  "1.0.0",
        "date":     __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "changes":  [
            "Initial build: merged indian_food.csv + Indian_Food_DF.csv",
            f"Total dishes: {len(final)}",
            "Added GI estimation, GL calculation, Ayurvedic dosha mapping",
            "Added ICMR RDA % per serving",
            "Validated macro energy consistency",
        ]
    })
    with open(CHANGELOG, "w") as f:
        json.dump(changelog, f, indent=2)
    print(f"  ✅ Changelog updated at {CHANGELOG}")


if __name__ == "__main__":
    main()
