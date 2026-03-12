"""
Nourish — Meal Planner
Selects dishes from nourish_foods.json to build daily meal plans.
Supports: diet filter, medical condition rules, regional preference, festival awareness.
"""

from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional
from .nutrient_engine import NutrientEngine, UserProfile, NutritionTargets

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH  = DATA_DIR / "nourish_foods.json"

# Festival fasting rules: (veg_only, avoid_grains, allowed_courses)
FESTIVAL_RULES = {
    "navratri":  {"veg_only": True, "avoid_grains": True, "allowed_courses": ["snack", "dessert", "main course"]},
    "ekadashi":  {"veg_only": True, "avoid_grains": True, "avoid_lentils": True},
    "ramadan":   {"veg_only": False,"two_meals": True, "meal_names": ["Suhoor", "Iftar"]},
    "onam":      {"veg_only": True, "region_filter": "South"},
    "pongal":    {"veg_only": True, "region_filter": "South"},
    "none":      {},
}

REGIONAL_PREFERENCES = {
    "North":      ["Punjab", "Delhi", "Uttar Pradesh", "Haryana", "Uttarakhand", "Himachal Pradesh", "Jammu and Kashmir"],
    "South":      ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana"],
    "East":       ["West Bengal", "Odisha", "Bihar", "Jharkhand", "Assam"],
    "West":       ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    "Central":    ["Madhya Pradesh", "Chhattisgarh"],
    "Northeast":  ["Manipur", "Nagaland", "Meghalaya", "Mizoram", "Tripura", "Sikkim", "Arunachal Pradesh"],
}

COURSE_MEAL_WEIGHTS = {
    "breakfast":     {"breakfast": 0.6, "snack": 0.3, "main course": 0.1},
    "lunch":         {"main course": 0.6, "breakfast": 0.1, "snack": 0.1, "dessert": 0.1, "starter": 0.1},
    "dinner":        {"main course": 0.7, "starter": 0.1, "dessert": 0.1, "snack": 0.1},
    "mid-morning":   {"snack": 0.7, "breakfast": 0.3},
    "evening snack": {"snack": 0.9, "dessert": 0.1},
    "suhoor":        {"breakfast": 0.7, "main course": 0.3},
    "iftar":         {"main course": 0.5, "snack": 0.3, "dessert": 0.2},
}


class MealPlanner:

    def __init__(self):
        with open(DB_PATH, encoding="utf-8") as f:
            db = json.load(f)
        self._all_foods: list[dict] = db["foods"]
        self._engine = NutrientEngine()

    def build_daily_plan(
        self,
        profile: UserProfile,
        targets: NutritionTargets,
        festival: str = "none",
        day_seed: int = 0,
    ) -> dict:
        """Build a full day meal plan for the given profile."""
        rng   = random.Random(day_seed)
        rules = self._engine.medical_filters(profile.medical)
        fest  = FESTIVAL_RULES.get(festival.lower(), {})
        meals = self._engine.meal_split(profile, targets)

        pool  = self._filtered_pool(profile, rules, fest)
        plan  = []

        for meal in meals:
            name_lower = meal["name"].lower()
            dishes     = self._pick_dishes(
                pool=pool,
                meal_name=name_lower,
                target_kcal=meal["target_kcal"],
                rules=rules,
                rng=rng,
                n_dishes=2,
            )
            plan.append({
                "meal":          meal["name"],
                "time":          meal["time"],
                "target_kcal":   meal["target_kcal"],
                "dishes":        dishes,
                "actual_kcal":   sum(d["kcal"] or 0 for d in dishes),
                "actual_protein_g": sum(d.get("protein_g") or 0 for d in dishes),
                "actual_carbs_g":   sum(d.get("carbs_g")   or 0 for d in dishes),
                "actual_fat_g":     sum(d.get("fat_g")     or 0 for d in dishes),
            })

        total_kcal    = sum(m["actual_kcal"]    for m in plan)
        total_protein = sum(m["actual_protein_g"] for m in plan)
        total_carbs   = sum(m["actual_carbs_g"]   for m in plan)
        total_fat     = sum(m["actual_fat_g"]     for m in plan)

        return {
            "date_seed":     day_seed,
            "festival":      festival,
            "meals":         plan,
            "daily_totals":  {
                "kcal":      round(total_kcal),
                "protein_g": round(total_protein, 1),
                "carbs_g":   round(total_carbs, 1),
                "fat_g":     round(total_fat, 1),
            },
            "target_kcal":   targets.target_kcal,
        }

    def build_weekly_plan(
        self,
        profile: UserProfile,
        targets: NutritionTargets,
        festival: str = "none",
        start_seed: int = 1000,
    ) -> list[dict]:
        """Build 7 days of meal plans."""
        days = []
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        for i, day_name in enumerate(day_names):
            day_plan = self.build_daily_plan(profile, targets, festival, seed=start_seed + i)
            day_plan["day"]  = day_name
            day_plan["day_num"] = i + 1
            days.append(day_plan)
        return days

    def search_foods(
        self,
        query: str = "",
        diet: str  = "all",
        course: str = "all",
        max_kcal: Optional[float] = None,
        max_gi: Optional[int] = None,
        region: str = "all",
        limit: int  = 50,
    ) -> list[dict]:
        """Food Explorer — search/filter the full database."""
        results = []
        q = query.lower().strip()

        for food in self._all_foods:
            if q and q not in food["name"].lower() and q not in (food.get("ingredients","") or "").lower():
                continue
            if diet != "all":
                is_veg = "non" not in food.get("diet","")
                if diet == "veg" and not is_veg:
                    continue
                if diet == "nonveg" and is_veg:
                    continue
            if course != "all" and food.get("course","").lower() != course.lower():
                continue
            if max_kcal and (food.get("kcal") or 0) > max_kcal:
                continue
            if max_gi and food.get("gi") and food["gi"] > max_gi:
                continue
            if region != "all":
                states = [s.lower() for s in REGIONAL_PREFERENCES.get(region, [])]
                if food.get("state","").lower() not in states and food.get("region","").lower() != region.lower():
                    continue
            results.append(food)
            if len(results) >= limit:
                break

        return results

    def scale_for_family(self, plan: dict, servings: int) -> dict:
        """Scale a meal plan for a family (Priority ⑤ — Family Mode)."""
        scaled = json.loads(json.dumps(plan))  # deep copy
        for meal in scaled.get("meals", []):
            meal["target_kcal"] *= servings
            meal["actual_kcal"] *= servings
            for d in meal.get("dishes", []):
                for key in ["kcal", "kj", "protein_g", "carbs_g", "fat_g", "fiber_g"]:
                    if d.get(key) is not None:
                        d[key] = round(d[key] * servings, 1)
        totals = scaled.get("daily_totals", {})
        for k in totals:
            totals[k] = round(totals[k] * servings, 1)
        scaled["servings"] = servings
        return scaled

    # ── Private ────────────────────────────────────────────────────────────────

    def _filtered_pool(self, profile: UserProfile, rules: dict, fest: dict) -> list[dict]:
        pool = []
        user_states = REGIONAL_PREFERENCES.get(profile.region, [])

        for food in self._all_foods:
            if not food.get("kcal"):
                continue
            diet_ok = self._diet_ok(food, profile.diet, fest)
            if not diet_ok:
                continue
            if rules.get("max_gi") and food.get("gi") and food["gi"] > rules["max_gi"]:
                continue
            if rules.get("low_sodium") and (food.get("salt_g") or 0) > 1.5:
                continue
            if fest.get("avoid_grains") and food.get("course","") in ("bread", "rice"):
                continue
            # Regional preference: prefer regional foods (not exclusive)
            food["_regional"] = food.get("state","") in user_states
            pool.append(food)

        return pool

    def _diet_ok(self, food: dict, user_diet: str, fest: dict) -> bool:
        is_veg = "non" not in food.get("diet","")
        if fest.get("veg_only") and not is_veg:
            return False
        if user_diet == "vegetarian" and not is_veg:
            return False
        return True

    def _pick_dishes(
        self,
        pool:        list[dict],
        meal_name:   str,
        target_kcal: float,
        rules:       dict,
        rng:         random.Random,
        n_dishes:    int = 2,
    ) -> list[dict]:
        weights = COURSE_MEAL_WEIGHTS.get(meal_name, {"main course": 1.0})
        target_per = target_kcal / n_dishes
        window     = 0.35  # ±35% of target_per

        # Build weighted sub-pool by course
        sub_pool = []
        for food in pool:
            course  = (food.get("course") or "").lower()
            w       = weights.get(course, 0.05)
            kcal    = food.get("kcal", 0) or 0
            lo, hi  = target_per * (1 - window), target_per * (1 + window)
            if lo <= kcal <= hi:
                sub_pool.extend([food] * max(1, int(w * 10)))

        # Prefer regional foods
        regional = [f for f in sub_pool if f.get("_regional")]
        if len(regional) >= n_dishes:
            sub_pool = regional * 2 + sub_pool  # boost regional

        if len(sub_pool) < n_dishes:
            sub_pool = pool  # fallback

        picked = []
        used   = set()
        attempts = 0
        while len(picked) < n_dishes and attempts < 200:
            attempts += 1
            food = rng.choice(sub_pool)
            if food["id"] not in used:
                used.add(food["id"])
                picked.append({
                    "id":         food["id"],
                    "name":       food["name"],
                    "kcal":       food.get("kcal"),
                    "kj":         food.get("kj"),
                    "protein_g":  food.get("protein_g"),
                    "carbs_g":    food.get("carbs_g"),
                    "fat_g":      food.get("fat_g"),
                    "fiber_g":    food.get("fiber_g"),
                    "gi":         food.get("gi"),
                    "gl":         food.get("gl"),
                    "course":     food.get("course"),
                    "region":     food.get("region"),
                    "state":      food.get("state"),
                    "flavor":     food.get("flavor"),
                    "diet":       food.get("diet"),
                    "ingredients": food.get("ingredients"),
                    "prep_min":   food.get("prep_min"),
                    "cook_min":   food.get("cook_min"),
                    "confidence": food.get("confidence"),
                })

        return picked
