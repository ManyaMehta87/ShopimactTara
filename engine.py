"""engine.py - the "brain" of ShopImpact.

Pure Python (lists, dicts, control structures, datetime). It never imports
Streamlit, so every function can be unit-tested on its own.

Core idea:  CO2 estimate (kg) = price in USD x product multiplier
            (x 0.85 if the brand is ethical)
"""
from collections import defaultdict
from datetime import date

import data


# ---------------------------------------------------------------------------
# Impact calculation
# ---------------------------------------------------------------------------
def to_usd(price, currency):
    """Convert a price in the chosen currency to USD (multipliers are per USD)."""
    return price * data.CURRENCIES[currency]["to_usd"]


def is_ethical_brand(brand, ticked=False):
    """A brand is ethical if the user ticked the box or it is on our curated list."""
    if ticked:
        return True
    return brand.strip().lower() in data.ETHICAL_BRANDS


def calculate_impact(price, currency, product_type, ethical=False):
    """Return the estimated CO2e in kg for one purchase."""
    if price <= 0:
        return 0.0
    multiplier = data.PRODUCT_TYPES[product_type]["multiplier"]
    co2 = to_usd(price, currency) * multiplier
    if ethical:
        co2 *= data.ETHICAL_BRAND_FACTOR
    return round(co2, 2)


def is_eco_tier(product_type):
    """True when the product type itself is a low-impact kind of item."""
    return data.PRODUCT_TYPES[product_type]["multiplier"] <= data.ECO_THRESHOLD


def is_green_choice(product_type, ethical):
    """A green choice = low-impact product type OR an ethical brand."""
    return is_eco_tier(product_type) or ethical


def make_purchase(product_type, brand, price, currency, purchase_date=None, ethical_ticked=False, note=""):
    """Build one purchase record (a dictionary) ready to store in the list."""
    brand = brand.strip() or "Unbranded / local"
    ethical = is_ethical_brand(brand, ethical_ticked)
    return {
        "date": purchase_date or date.today(),
        "type": product_type,
        "brand": brand,
        "price": round(float(price), 2),
        "currency": currency,
        "ethical": ethical,
        "second_life": data.PRODUCT_TYPES[product_type]["second_life"],
        "green": is_green_choice(product_type, ethical),
        "co2": calculate_impact(price, currency, product_type, ethical),
        "note": str(note).strip(),
    }


# ---------------------------------------------------------------------------
# Suggestions and what-if savings
# ---------------------------------------------------------------------------
def greener_alternatives(product_type):
    """The list of suggestion dictionaries for a product type."""
    return data.ALTERNATIVES.get(product_type, [])


def swap_saving(price, currency, product_type, ethical=False):
    """If a greener type exists, return (swap_type, kg_saved); else (None, 0)."""
    swap = data.PRODUCT_TYPES[product_type]["swap_to"]
    if swap is None:
        return None, 0.0
    now = calculate_impact(price, currency, product_type, ethical)
    then = calculate_impact(price, currency, swap, ethical)
    return swap, round(max(now - then, 0.0), 2)


def equivalents(kg):
    """Friendly real-world comparisons (approximate)."""
    return {
        "km_driven": round(kg / data.KG_CO2_PER_KM_DRIVEN),
        "tree_months": round(kg / data.KG_CO2_ABSORBED_PER_TREE_PER_MONTH, 1),
    }


# ---------------------------------------------------------------------------
# Monthly summary
# ---------------------------------------------------------------------------
def purchases_in_month(purchases, year, month):
    return [p for p in purchases if p["date"].year == year and p["date"].month == month]


def monthly_summary(purchases, year, month, avoided=None):
    """Totals for one month. Spend is converted to USD so currencies can mix."""
    items = purchases_in_month(purchases, year, month)
    avoided_items = purchases_in_month(avoided or [], year, month)
    by_category = defaultdict(float)
    total_co2 = 0.0
    total_spend_usd = 0.0
    for p in items:                                    # control structure: loop
        total_co2 += p["co2"]
        total_spend_usd += to_usd(p["price"], p["currency"])
        by_category[p["type"]] += p["co2"]
    count = len(items)
    green = sum(1 for p in items if p["green"])
    return {
        "count": count,
        "total_co2": round(total_co2, 2),
        "total_spend_usd": round(total_spend_usd, 2),
        "avg_co2": round(total_co2 / count, 2) if count else 0.0,
        "green_share": round(100 * green / count) if count else 0,
        "ethical_count": sum(1 for p in items if p["ethical"]),
        "second_life_count": sum(1 for p in items if p["second_life"]),
        "by_category": dict(by_category),
        "avoided_count": len(avoided_items),
        "avoided_co2": round(sum(a["co2"] for a in avoided_items), 2),
    }


def footprint_status(total_co2, goal):
    """Traffic-light status of the month: 'green', 'amber' or 'red'."""
    if goal <= 0:
        return "amber"
    ratio = total_co2 / goal
    if ratio <= 0.75:
        return "green"
    if ratio <= 1.0:
        return "amber"
    return "red"


# ---------------------------------------------------------------------------
# Badge rules: one small function per badge, stored in a dictionary.
# Every rule receives (purchases, summary_for_selected_month, monthly_goal).
# ---------------------------------------------------------------------------
def _rule_first_step(purchases, s, goal):
    return len(purchases) >= 1


def _rule_tracker(purchases, s, goal):
    return len(purchases) >= 10


def _rule_low_impact(purchases, s, goal):
    return s["count"] >= 3 and s["total_co2"] <= goal


def _rule_eco_saver(purchases, s, goal):
    return s["count"] >= 5 and s["total_co2"] <= 0.5 * goal and s["green_share"] >= 60


def _rule_ethical(purchases, s, goal):
    return s["ethical_count"] >= 3


def _rule_second_life(purchases, s, goal):
    return s["second_life_count"] >= 2


def _rule_green_streak(purchases, s, goal):
    ordered = sorted(purchases, key=lambda p: p["date"])   # latest last
    last_three = ordered[-3:]
    return len(last_three) == 3 and all(p["green"] for p in last_three)


def _rule_mindful_pause(purchases, s, goal):
    return s["avoided_count"] >= 1


BADGE_RULES = {
    "first_step": _rule_first_step,
    "tracker": _rule_tracker,
    "low_impact": _rule_low_impact,
    "eco_saver": _rule_eco_saver,
    "ethical": _rule_ethical,
    "second_life": _rule_second_life,
    "green_streak": _rule_green_streak,
    "mindful_pause": _rule_mindful_pause,
}


def evaluate_badges(purchases, year, month, goal, avoided=None):
    """Return the list of badge ids currently earned."""
    summary = monthly_summary(purchases, year, month, avoided)
    return [badge_id for badge_id, rule in BADGE_RULES.items() if rule(purchases, summary, goal)]


def new_badges(before, after):
    """Badge ids that are in `after` but were not in `before`."""
    return [b for b in after if b not in before]


# ---------------------------------------------------------------------------
# kindcart extras: impact decoder, transparency, budget swaps, comparisons, goals
# ---------------------------------------------------------------------------
def impact_level(product_type):
    """'Low', 'Medium' or 'High' for the product type itself."""
    m = data.PRODUCT_TYPES[product_type]["multiplier"]
    if m <= data.IMPACT_LOW_MAX:
        return "Low"
    if m <= data.IMPACT_MEDIUM_MAX:
        return "Medium"
    return "High"


def impact_score(product_type):
    """0-100 score for the impact meter (100 = highest multiplier we know)."""
    m = data.PRODUCT_TYPES[product_type]["multiplier"]
    return min(100, round(100 * m / data.IMPACT_SCORE_MAX_MULTIPLIER))


def explain_equivalents(kg):
    """Impact Explained: turn kilograms into things people can picture (approximate)."""
    eq = equivalents(kg)
    eq["phone_charges"] = round(kg / data.KG_CO2_PER_PHONE_CHARGE)
    return eq


def explain_impact(price, currency, product_type, ethical=False):
    """Transparency Notes: plain-English lines showing how the number was produced."""
    info = data.PRODUCT_TYPES[product_type]
    usd = to_usd(price, currency)
    base = round(usd * info["multiplier"], 2)
    notes = [f"Calculation: about ${usd:,.2f} x {info['multiplier']} kg CO2e per $ = {base} kg."]
    if ethical:
        notes.append(f"Ethical-brand adjustment: x {data.ETHICAL_BRAND_FACTOR} "
                     "(self-declared or from our small curated list, not independently verified).")
    notes.append("Status: ESTIMATED. The multiplier is an illustrative average for this type of product, "
                 "not a measurement for this exact item or brand.")
    return notes


def budget_swaps(price, budget, currency, product_type):
    """Green Within My Budget: greener types (following the swap chain), their
    estimated cost, the kg saved, and whether they fit the budget."""
    out = []
    now = calculate_impact(price, currency, product_type)
    current = data.PRODUCT_TYPES[product_type]["swap_to"]
    while current is not None:                                   # walk the chain
        est_cost = round(price * data.PRICE_FACTOR[current] / data.PRICE_FACTOR[product_type], 2)
        alt = calculate_impact(est_cost, currency, current)
        out.append({"type": current, "est_cost": est_cost, "saved": round(max(now - alt, 0.0), 2),
                    "fits": est_cost <= budget})
        current = data.PRODUCT_TYPES[current]["swap_to"]
    return sorted(out, key=lambda r: r["saved"], reverse=True)


def previous_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)


def compare_months(purchases, year, month):
    """Monthly Progress: this month's CO2 against last month's."""
    now = monthly_summary(purchases, year, month)
    py, pm = previous_month(year, month)
    prev = monthly_summary(purchases, py, pm)
    change = None
    if prev["count"] and prev["total_co2"] > 0:
        change = round(100 * (now["total_co2"] - prev["total_co2"]) / prev["total_co2"])
    return {"prev_total": prev["total_co2"], "prev_count": prev["count"], "change_pct": change}


def make_avoided(product_type, price, currency, purchase_date=None):
    """A paused purchase: the CO2 you did NOT emit by thinking twice."""
    return {"date": purchase_date or date.today(), "type": product_type, "price": round(float(price), 2),
            "currency": currency, "co2": calculate_impact(price, currency, product_type)}


def quick_add_items(purchases, n=3):
    """Quick Add: the n most recent distinct (type, brand) combinations with their last price."""
    seen, out = set(), []
    for p in reversed(purchases):
        key = (p["type"], p["brand"])
        if key not in seen:
            seen.add(key)
            out.append(p)
        if len(out) == n:
            break
    return out


def goal_progress(goal_id, summary, goal_kg):
    """Personal Eco Goals: returns (current, target, done) for one goal id."""
    if goal_id == "second_life":
        cur, tgt = summary["second_life_count"], data.GOALS[goal_id]["target"]
        return cur, tgt, cur >= tgt
    if goal_id == "green_share":
        cur = summary["green_share"] if summary["count"] >= 3 else 0
        return cur, 60, cur >= 60
    if goal_id == "pause":
        cur, tgt = summary["avoided_count"], data.GOALS[goal_id]["target"]
        return cur, tgt, cur >= tgt
    if goal_id == "under_goal":
        done = summary["count"] >= 3 and summary["total_co2"] <= goal_kg
        return summary["total_co2"], goal_kg, done
    return 0, 1, False


# ---------------------------------------------------------------------------
# Demo data used for testing / marking
# ---------------------------------------------------------------------------
def demo_purchases(today=None):
    """15 realistic purchases (cheap/expensive, eco/non-eco) over two months."""
    today = today or date.today()
    this_month = today.replace(day=1)
    last_month = (this_month.replace(day=1) - (date.resolution)).replace(day=1)
    rows = [
        # (month_anchor, day, type, brand, price, ethical)
        (last_month, 3, "Fast-fashion clothing", "QuickStyle", 45, False),
        (last_month, 6, "Meat & dairy groceries", "Local Mart", 38, False),
        (last_month, 9, "New electronics", "TechNova", 520, False),
        (last_month, 14, "Leather shoes", "StepRight", 120, False),
        (last_month, 20, "Packaged snacks", "SnackCo", 12, False),
        (last_month, 25, "Second-hand books", "Oxfam", 9, True),
        (this_month, 1, "Second-hand clothing", "Thrift", 22, True),
        (this_month, 2, "Local seasonal produce", "Farmers Market", 18, True),
        (this_month, 3, "Plant-based groceries", "GreenBasket", 30, False),
        (this_month, 4, "Refurbished electronics", "ReNew", 80, False),
        (this_month, 5, "Reusable household goods", "Local Market", 15, True),
        (this_month, 6, "Recycled-material shoes", "Veja", 60, True),
        (this_month, 7, "Refill / zero-waste cosmetics", "The Body Shop", 20, True),
        (this_month, 8, "Second-hand furniture", "Thrift", 60, True),
        (this_month, 9, "Local seasonal produce", "Farmers Market", 14, True),
    ]
    out = []
    for anchor, day, ptype, brand, price, ethical in rows:
        d = anchor.replace(day=min(day, 28))
        out.append(make_purchase(ptype, brand, price, "USD ($)", d, ethical))
    return out


def demo_avoided(today=None):
    """One paused purchase this month for the demo."""
    today = today or date.today()
    return [make_avoided("New electronics", 150, "USD ($)", today.replace(day=min(today.day, 28)))]
