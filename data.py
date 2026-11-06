"""data.py - all the curated "knowledge" ShopImpact uses.

Keeping data separate from logic (engine.py) and UI (app.py) makes the project
modular: to add a product type you only edit this file.

IMPORTANT: multipliers are ILLUSTRATIVE spend-based estimates (kg CO2e per
1 US dollar spent), inspired by the idea behind spend-based emission factors.
They are designed to show relative differences between choices, not to be a
lab-grade carbon audit.
"""

# ---------------------------------------------------------------------------
# 1. Currency handling: multipliers are per USD, so other currencies are
#    converted first. Rates are approximate and cosmetic for this project.
# ---------------------------------------------------------------------------
CURRENCIES = {
    "USD ($)": {"symbol": "$", "to_usd": 1.00},
    "INR (\u20b9)": {"symbol": "\u20b9", "to_usd": 0.012},
    "EUR (\u20ac)": {"symbol": "\u20ac", "to_usd": 1.08},
    "GBP (\u00a3)": {"symbol": "\u00a3", "to_usd": 1.27},
}

# ---------------------------------------------------------------------------
# 2. Product types: dictionary of dictionaries.
#    multiplier  -> kg CO2e per USD spent
#    group       -> family of products (used to find greener swaps)
#    second_life -> True if the item is second-hand / refurbished / refill
#    swap_to     -> key of the greener type in the same family (or None)
# ---------------------------------------------------------------------------
PRODUCT_TYPES = {
    "Fast-fashion clothing":      {"icon": "\U0001F455", "multiplier": 0.50, "group": "Clothing",    "second_life": False, "swap_to": "Second-hand clothing"},
    "Second-hand clothing":       {"icon": "\U0001F9E5", "multiplier": 0.08, "group": "Clothing",    "second_life": True,  "swap_to": None},
    "Leather shoes":              {"icon": "\U0001F45E", "multiplier": 0.70, "group": "Footwear",    "second_life": False, "swap_to": "Recycled-material shoes"},
    "Recycled-material shoes":    {"icon": "\U0001F45F", "multiplier": 0.25, "group": "Footwear",    "second_life": False, "swap_to": None},
    "New electronics":            {"icon": "\U0001F4F1", "multiplier": 0.45, "group": "Electronics", "second_life": False, "swap_to": "Refurbished electronics"},
    "Refurbished electronics":    {"icon": "\U0001F50B", "multiplier": 0.15, "group": "Electronics", "second_life": True,  "swap_to": None},
    "Meat & dairy groceries":     {"icon": "\U0001F969", "multiplier": 0.90, "group": "Food",        "second_life": False, "swap_to": "Plant-based groceries"},
    "Packaged snacks":            {"icon": "\U0001F36B", "multiplier": 0.35, "group": "Food",        "second_life": False, "swap_to": "Local seasonal produce"},
    "Plant-based groceries":      {"icon": "\U0001F966", "multiplier": 0.20, "group": "Food",        "second_life": False, "swap_to": "Local seasonal produce"},
    "Local seasonal produce":     {"icon": "\U0001F34E", "multiplier": 0.12, "group": "Food",        "second_life": False, "swap_to": None},
    "Single-use plastic goods":   {"icon": "\U0001F964", "multiplier": 0.60, "group": "Household",   "second_life": False, "swap_to": "Reusable household goods"},
    "Reusable household goods":   {"icon": "\u267B\ufe0f", "multiplier": 0.10, "group": "Household", "second_life": True,  "swap_to": None},
    "New furniture":              {"icon": "\U0001F6CB\ufe0f", "multiplier": 0.40, "group": "Furniture", "second_life": False, "swap_to": "Second-hand furniture"},
    "Second-hand furniture":      {"icon": "\U0001FA91", "multiplier": 0.07, "group": "Furniture",   "second_life": True,  "swap_to": None},
    "Conventional cosmetics":     {"icon": "\U0001F484", "multiplier": 0.30, "group": "Personal care", "second_life": False, "swap_to": "Refill / zero-waste cosmetics"},
    "Refill / zero-waste cosmetics": {"icon": "\U0001F9F4", "multiplier": 0.12, "group": "Personal care", "second_life": True, "swap_to": None},
    "New books":                  {"icon": "\U0001F4D8", "multiplier": 0.18, "group": "Books",       "second_life": False, "swap_to": "Second-hand books"},
    "Second-hand books":          {"icon": "\U0001F4DA", "multiplier": 0.05, "group": "Books",       "second_life": True,  "swap_to": None},
}

# A product type with a multiplier at or below this value is an "eco-tier" choice.
ECO_THRESHOLD = 0.20

# Buying from an ethical brand trims the estimated footprint by this factor.
ETHICAL_BRAND_FACTOR = 0.85

# ---------------------------------------------------------------------------
# 3. Greener alternatives: a LIST of suggestions for every product type.
#    (Examples of approaches and sample brands; always check a brand's own
#    sustainability claims before trusting them.)
# ---------------------------------------------------------------------------
ALTERNATIVES = {
    "Fast-fashion clothing": [
        {"name": "Local thrift / charity shop", "why": "Clothes get a second life, no new production."},
        {"name": "Clothes-swap with friends", "why": "Zero money, near-zero carbon."},
        {"name": "Patagonia (Worn Wear)", "why": "Repair-first brand with a used-gear programme."},
    ],
    "Second-hand clothing": [
        {"name": "Keep it up!", "why": "You are already on the greenest shelf."},
    ],
    "Leather shoes": [
        {"name": "Veja", "why": "Publishes sourcing info; uses recycled and organic materials."},
        {"name": "Allbirds", "why": "Reports product footprints on its labels."},
        {"name": "Resoled / second-hand shoes", "why": "Extends the life of a pair."},
    ],
    "Recycled-material shoes": [
        {"name": "Keep it up!", "why": "Recycled materials are a strong choice."},
    ],
    "New electronics": [
        {"name": "Certified refurbished phone / laptop", "why": "Avoids the large manufacturing footprint."},
        {"name": "Repair your current device", "why": "Extending life by 1 year cuts impact a lot."},
        {"name": "Fairphone", "why": "Modular and repairable design."},
    ],
    "Refurbished electronics": [
        {"name": "Keep it up!", "why": "Refurbished devices skip most manufacturing emissions."},
    ],
    "Meat & dairy groceries": [
        {"name": "Plant-based protein (lentils, beans, tofu)", "why": "Far lower emissions per meal."},
        {"name": "Oat / soy milk", "why": "Lower footprint than dairy milk."},
        {"name": "Meat-free Mondays", "why": "A small habit with a big total effect."},
    ],
    "Packaged snacks": [
        {"name": "Bulk-bin nuts and seeds", "why": "Less packaging and processing."},
        {"name": "Seasonal fruit", "why": "Minimal packaging, short supply chain."},
    ],
    "Plant-based groceries": [
        {"name": "Local farmers' market", "why": "Fewer food-miles."},
    ],
    "Local seasonal produce": [
        {"name": "Keep it up!", "why": "Local and seasonal is one of the lowest-impact baskets."},
    ],
    "Single-use plastic goods": [
        {"name": "Reusable bottle / cutlery / bags", "why": "Pays off after a few uses."},
        {"name": "Refill stations", "why": "Cuts plastic packaging."},
    ],
    "Reusable household goods": [
        {"name": "Keep it up!", "why": "Reusables are a great habit."},
    ],
    "New furniture": [
        {"name": "Second-hand marketplace", "why": "Solid furniture often outlasts new flat-pack."},
        {"name": "FSC-certified wood", "why": "Responsibly managed forests."},
    ],
    "Second-hand furniture": [
        {"name": "Keep it up!", "why": "Giving furniture another life is excellent."},
    ],
    "Conventional cosmetics": [
        {"name": "Refill / solid-bar products", "why": "Less plastic and water transport."},
        {"name": "The Body Shop (refill stations)", "why": "Refill scheme in many stores."},
    ],
    "Refill / zero-waste cosmetics": [
        {"name": "Keep it up!", "why": "Refills cut packaging waste."},
    ],
    "New books": [
        {"name": "Public library", "why": "One book, many readers."},
        {"name": "Second-hand bookshop", "why": "Cheap and low-carbon."},
    ],
    "Second-hand books": [
        {"name": "Keep it up!", "why": "Pre-loved books are a green classic."},
    ],
}

# Brands treated as "ethical" automatically (case-insensitive). The user can
# also tick a checkbox for any other brand they know to be certified.
ETHICAL_BRANDS = {
    "patagonia", "veja", "allbirds", "fairphone", "the body shop",
    "thrift", "local market", "farmers market", "library", "oxfam",
}

# ---------------------------------------------------------------------------
# 4. Badges. The rules live in engine.py; this is the display information.
# ---------------------------------------------------------------------------
BADGES = {
    "first_step":    {"emoji": "\U0001F331", "name": "First Step",           "how": "Log your first purchase."},
    "tracker":       {"emoji": "\U0001F4CA", "name": "Footprint Tracker",    "how": "Log 10 purchases in total."},
    "low_impact":    {"emoji": "\U0001F343", "name": "Low Impact Shopper",   "how": "Stay under your monthly CO\u2082 goal with 3+ purchases."},
    "eco_saver":     {"emoji": "\U0001F3C6", "name": "Eco Saver of the Month", "how": "Use at most half your CO\u2082 goal, 5+ purchases, 60%+ green choices."},
    "ethical":       {"emoji": "\U0001F91D", "name": "Ethical Brand Champion", "how": "Buy from 3+ ethical brands in a month."},
    "second_life":   {"emoji": "\u267B\ufe0f", "name": "Second-Life Hero",   "how": "Buy 2+ second-hand, refurbished or refill items in a month."},
    "green_streak":  {"emoji": "\U0001F525", "name": "Green Streak",         "how": "Make 3 green choices in a row."},
}

# ---------------------------------------------------------------------------
# 5. Rotating content: eco tips and motivational quotes (optional features).
# ---------------------------------------------------------------------------
ECO_TIPS = [
    "Did you know? Extending the life of a phone by one year can save a big chunk of its lifetime emissions.",
    "Did you know? Second-hand clothes avoid the water and energy used to make new fabric.",
    "Bamboo grows fast and needs little water, which often gives it a lower footprint than many hardwoods.",
    "Washing clothes in cold water uses much less energy than hot.",
    "Buying less but better is often the single biggest carbon saver.",
    "A reusable bottle pays back its footprint after a few dozen uses.",
    "Local, seasonal food usually travels fewer miles and needs less storage.",
    "Repairing something is almost always greener than replacing it.",
    "Libraries are free, shared and low-carbon: one book, many readers.",
    "Plant-based meals are usually lower-carbon than meat-heavy ones.",
]

QUOTES = [
    "Small choices, repeated, change the world.",
    "You don't need to be perfect. You just need to be curious.",
    "Every green choice is a vote for the future you want.",
    "Progress beats perfection, one purchase at a time.",
    "The planet doesn't need a few people doing it perfectly. It needs many doing it kindly.",
    "Look after the Earth: it's the only shop that never restocks.",
]

# Approximate real-world equivalents (labelled "approx." in the UI).
KG_CO2_PER_KM_DRIVEN = 0.21
KG_CO2_ABSORBED_PER_TREE_PER_MONTH = 1.75   # about 21 kg per tree per year

DEFAULT_MONTHLY_GOAL_KG = 60.0


# ===========================================================================
# 6. kindcart additions: budget logic, impact levels, goals, garden
# ===========================================================================
# Typical price (in USD) used as a sensible default when a product type is chosen (Quick Add).
TYPICAL_PRICE_USD = {
    "Fast-fashion clothing": 30, "Second-hand clothing": 12, "Leather shoes": 90,
    "Recycled-material shoes": 80, "New electronics": 300, "Refurbished electronics": 180,
    "Meat & dairy groceries": 25, "Packaged snacks": 6, "Plant-based groceries": 20,
    "Local seasonal produce": 12, "Single-use plastic goods": 8, "Reusable household goods": 15,
    "New furniture": 200, "Second-hand furniture": 80, "Conventional cosmetics": 15,
    "Refill / zero-waste cosmetics": 14, "New books": 15, "Second-hand books": 5,
}

# Typical price relative to the conventional version (1.0 = same price).
# Illustrative: used for "Green Within My Budget" so the app never assumes green = expensive.
PRICE_FACTOR = {name: 1.0 for name in PRODUCT_TYPES}
PRICE_FACTOR.update({
    "Second-hand clothing": 0.40, "Recycled-material shoes": 1.15, "Refurbished electronics": 0.65,
    "Plant-based groceries": 0.80, "Local seasonal produce": 0.85, "Reusable household goods": 1.30,
    "Second-hand furniture": 0.50, "Refill / zero-waste cosmetics": 0.90, "Second-hand books": 0.40,
})

# Impact levels (kg CO2e per USD): Low <= 0.20 < Medium <= 0.45 < High
IMPACT_LOW_MAX = 0.20
IMPACT_MEDIUM_MAX = 0.45
IMPACT_SCORE_MAX_MULTIPLIER = 0.90      # the highest multiplier = score 100

KG_CO2_PER_PHONE_CHARGE = 0.008          # about 8 g per full smartphone charge (approx.)

# Personal eco goals the user can pick (progress is computed in engine.goal_progress)
GOALS = {
    "second_life": {"emoji": "\u267B\ufe0f", "name": "Buy 2 second-hand, refurbished or refill items", "target": 2},
    "green_share": {"emoji": "\U0001F33F", "name": "Make 60% of my purchases green choices", "target": 60},
    "pause":       {"emoji": "\u23F8\ufe0f", "name": "Pause 1 impulse buy", "target": 1},
    "under_goal":  {"emoji": "\U0001F3AF", "name": "Stay under my monthly CO\u2082 goal (3+ purchases)", "target": None},
}
DEFAULT_GOAL_IDS = ["second_life", "pause"]

# Virtual garden: every badge earned grows one plant (same order as BADGES).
GARDEN_PLANTS = ["\U0001F331", "\U0001F33F", "\U0001F337", "\U0001F33B", "\U0001F333", "\U0001F338", "\U0001F340", "\U0001FAB4"]

BADGES["mindful_pause"] = {"emoji": "\u23F8\ufe0f", "name": "Mindful Pause",
                           "how": "Pause a purchase using 'Before you buy'."}

# Pip, the mascot: image file for each emotional state and the little mood pill text.
PIP_STATES = {
    "before":   {"file": "pip_before.png",   "pill": "Pip is curious \U0001F331"},
    "learning": {"file": "pip_learning.png", "pill": "Pip is learning \U0001F33F"},
    "excited":  {"file": "pip_excited.png",  "pill": "Pip is happy \U0001F31F"},
    "goal":     {"file": "pip_goal.png",     "pill": "Pip is thriving \U0001F333"},
}

# Things Pip says when you tap or hover over it (also mixed with eco tips and quotes).
PIP_CHATTER = [
    "Ooh! Let's check the impact of this one.",
    "Wait! I found another option you might like.",
    "One small choice, one happy planet!",
    "We're improving, not chasing perfection.",
    "LOOK AT US GROWING! \U0001F331",
    "Psst... second-hand finds are my favourite!",
    "Tap me anytime. I have lots of eco tips!",
    "Every green choice is a tiny hug for the Earth.",
]
