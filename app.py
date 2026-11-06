"""kindcart. - a ShopImpact experience (main Streamlit app).

Run locally:   streamlit run app.py

Pages (top navigation):  Home | Log a purchase | My impact | Green swaps | My achievements
Mascot: Pip the sprout reacts to what you do (4 emotional states, see mascot.py).
"""
import random
from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import data
import engine
import turtle_art
from mascot import logo_img, logo_path, pip_widget

st.set_page_config(page_title="kindcart.", page_icon=logo_path(), layout="wide")

HOME, LOG, IMPACT, SWAPS, ACH = ("\U0001F3E0 Home", "\u2795 Log a purchase", "\U0001F4CA My impact",
                                 "\U0001F504 Green swaps", "\U0001F3C5 My achievements")
PAGES = [HOME, LOG, IMPACT, SWAPS, ACH]
TODAY = date.today()


# ===========================================================================
# 1. STATE
# ===========================================================================
def init_state():
    s = st.session_state
    s.setdefault("purchases", [])            # list of purchase dictionaries
    s.setdefault("avoided", [])              # paused purchases ("Before you buy")
    s.setdefault("earned", [])               # badge ids
    s.setdefault("goals_done", [])           # personal goal ids completed
    s.setdefault("event", None)              # what happened on the last action
    s.setdefault("nonce", 0)                 # changes on every event -> replays turtle animation
    s.setdefault("tip", random.choice(data.ECO_TIPS))
    s.setdefault("quote", random.choice(data.QUOTES))
    s.setdefault("page", HOME)
    s.setdefault("currency", "USD ($)")
    s.setdefault("goal", data.DEFAULT_MONTHLY_GOAL_KG)
    s.setdefault("contrast", False)
    s.setdefault("my_goals", list(data.DEFAULT_GOAL_IDS))
    s.setdefault("view_month", (TODAY.year, TODAY.month))
    first = list(data.PRODUCT_TYPES)[0]
    s.setdefault("in_type", first)
    s.setdefault("in_brand", "")
    s.setdefault("in_price", float(data.TYPICAL_PRICE_USD[first]))
    s.setdefault("in_date", TODAY)
    s.setdefault("in_note", "")
    s.setdefault("in_ethical", False)
    s.setdefault("sw_type", "Fast-fashion clothing")
    s.setdefault("sw_price", 40.0)
    s.setdefault("sw_budget", 40.0)
    # Streamlit forgets widget values for widgets not drawn on the current page.
    # Re-assigning each key keeps the value alive while the user visits other pages.
    for key in ("in_type", "in_brand", "in_price", "in_date", "in_note", "in_ethical",
                "view_month", "sw_type", "sw_price", "sw_budget"):
        s[key] = s[key]


init_state()
S = st.session_state


def typical_price(product_type):
    """Sensible default price for a type, in the chosen currency (Quick Add)."""
    return round(data.TYPICAL_PRICE_USD[product_type] / data.CURRENCIES[S.currency]["to_usd"], 2)


def on_type_change():
    S.in_price = typical_price(S.in_type)


def on_currency_change():
    S.in_price = typical_price(S.in_type)
    S.sw_price = S.sw_budget = typical_price(S.sw_type)


def clear_event():
    S.event = None


def go(page):
    S.page = page
    S.event = None


def _record(p):
    """Store a purchase, refresh badges and goals, and remember what happened."""
    S.purchases.append(p)
    y, m = p["date"].year, p["date"].month
    before = list(S.earned)
    S.earned = list(dict.fromkeys(before + engine.evaluate_badges(S.purchases, y, m, S.goal, S.avoided)))
    summ = engine.monthly_summary(S.purchases, y, m, S.avoided)
    done_now = [g for g in S.my_goals if engine.goal_progress(g, summ, S.goal)[2]]
    new_goals = [g for g in done_now if g not in S.goals_done]
    S.goals_done += new_goals
    swap, saved = engine.swap_saving(p["price"], p["currency"], p["type"], p["ethical"])
    S.nonce += 1
    S.event = {"kind": "green" if p["green"] else "regular", "co2": p["co2"], "type": p["type"],
               "swap": swap, "saved": saved, "shown": False,
               "new_badges": engine.new_badges(before, S.earned), "new_goals": new_goals}
    S.tip = random.choice(data.ECO_TIPS)
    S.view_month = (y, m)
    st.toast("Purchase logged! \U0001F331")


def log_purchase():
    if S.in_price <= 0:
        S.event = {"kind": "error"}
        return
    _record(engine.make_purchase(S.in_type, S.in_brand, S.in_price, S.currency, S.in_date,
                                 S.in_ethical, S.in_note))
    S.in_brand, S.in_note, S.in_ethical = "", "", False


def quick_add(index):
    """One-tap re-log of a recent item (Quick Add)."""
    item = engine.quick_add_items(S.purchases)[index]
    _record(engine.make_purchase(item["type"], item["brand"], item["price"], item["currency"],
                                 TODAY, item["ethical"], ""))


def pause_purchase():
    """Before You Buy: log a paused purchase and the CO2 it avoided."""
    if S.in_price <= 0:
        S.event = {"kind": "error"}
        return
    a = engine.make_avoided(S.in_type, S.in_price, S.currency, S.in_date)
    S.avoided.append(a)
    before = list(S.earned)
    S.earned = list(dict.fromkeys(before + engine.evaluate_badges(
        S.purchases, a["date"].year, a["date"].month, S.goal, S.avoided)))
    summ = engine.monthly_summary(S.purchases, a["date"].year, a["date"].month, S.avoided)
    new_goals = [g for g in S.my_goals if g not in S.goals_done and engine.goal_progress(g, summ, S.goal)[2]]
    S.goals_done += new_goals
    S.nonce += 1
    S.event = {"kind": "paused", "co2": a["co2"], "type": a["type"], "shown": False,
               "new_badges": engine.new_badges(before, S.earned), "new_goals": new_goals}
    st.toast("Mindful pause! \u23F8\uFE0F")


def use_swap(product_type, cost):
    """Green swaps -> pre-fill the Log page with the chosen alternative."""
    S.in_type, S.in_price, S.in_brand = product_type, float(cost), ""
    go(LOG)


def load_demo():
    S.purchases, S.avoided = engine.demo_purchases(), engine.demo_avoided()
    S.earned = engine.evaluate_badges(S.purchases, TODAY.year, TODAY.month, S.goal, S.avoided)
    summ = engine.monthly_summary(S.purchases, TODAY.year, TODAY.month, S.avoided)
    S.goals_done = [g for g in S.my_goals if engine.goal_progress(g, summ, S.goal)[2]]
    S.event, S.nonce = None, S.nonce + 1
    S.view_month = (TODAY.year, TODAY.month)


def clear_all():
    S.purchases, S.avoided, S.earned, S.goals_done, S.event = [], [], [], [], None
    S.nonce += 1


def undo_last():
    if S.purchases:
        S.purchases.pop()
        S.event = None


# ===========================================================================
# 2. SIDEBAR  (settings and data tools)
# ===========================================================================
with st.sidebar:
    st.markdown("## \u2699\uFE0F Settings")
    st.selectbox("Currency", list(data.CURRENCIES), key="currency", on_change=on_currency_change)
    st.slider("My monthly CO\u2082 goal (kg)", 10, 200, step=5, key="goal",
              help="Badges, goals and the traffic-light status are measured against this.")
    st.multiselect("My personal eco goals", list(data.GOALS), key="my_goals",
                   format_func=lambda g: f"{data.GOALS[g]['emoji']} {data.GOALS[g]['name']}")
    st.toggle("High-contrast mode (bigger, bolder)", key="contrast")
    st.divider()
    st.button("\U0001F9EA Load demo data", on_click=load_demo, width="stretch")
    st.button("\u21A9\uFE0F Undo last purchase", on_click=undo_last, width="stretch")
    st.button("\U0001F5D1\uFE0F Clear everything", on_click=clear_all, width="stretch")
    if S.purchases:
        export = pd.DataFrame(S.purchases)[["date", "type", "brand", "price", "currency", "ethical", "note"]]
        st.download_button("\u2B07\uFE0F Download my journal (CSV)", export.to_csv(index=False),
                           file_name="kindcart_journal.csv", mime="text/csv", width="stretch")
    upload = st.file_uploader("Import a CSV", type="csv", help="Same columns as the download.")
    if upload is not None and st.button("Import file", width="stretch"):
        try:
            frame = pd.read_csv(upload)
            rows = [engine.make_purchase(r["type"], str(r["brand"]) if pd.notna(r["brand"]) else "",
                                         r["price"], r["currency"], pd.to_datetime(r["date"]).date(),
                                         bool(r["ethical"]),
                                         str(r["note"]) if "note" in frame and pd.notna(r["note"]) else "")
                    for _, r in frame.iterrows()]
            S.purchases.extend(rows)
            st.success(f"Imported {len(rows)} purchases.")
        except Exception:
            st.error("Sorry, I couldn't read that file. Please use a CSV downloaded from this app.")

# ===========================================================================
# 3. STYLE  (kindcart palette: sage, forest and soft cream)
# ===========================================================================
THEMES = {
    "soft": {"bg": "#FBFBF8", "card": "#FFFFFF", "text": "#25352B", "head": "#2F5D3E", "accent": "#6F9E7B",
             "banner": "#E9F1E3", "stat": "#F3F4F1", "sand": "#F5EFD8", "border": "#DCE6D6", "base": "17px"},
    "contrast": {"bg": "#FFFFFF", "card": "#FFFFFF", "text": "#000000", "head": "#0B3D1E", "accent": "#1B7A3A",
                 "banner": "#DDF0D8", "stat": "#EEF2EE", "sand": "#FFF4CC", "border": "#000000", "base": "20px"},
}
T = THEMES["contrast" if S.contrast else "soft"]
CSS = """
<style>
 @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
 html, body, .stApp, [class*="css"] {font-family: 'Montserrat', 'Segoe UI', sans-serif;}
 .stApp {background: __bg__; color: __text__;}
 html, body, .stMarkdown p, label {font-size: __base__ !important; color: __text__;}
 h1, h2, h3 {color: __head__; letter-spacing: -0.5px;}
 div[data-testid="stVerticalBlockBorderWrapper"] {background: __card__; border-radius: 20px; border: 2px solid __border__;}
 div[data-testid="stMetric"] {background: __stat__; border-radius: 18px; padding: 12px 18px;}
 div[data-testid="stMetricValue"] {font-size: 2.1rem !important; color: __head__; font-weight: 800;}
 .stButton > button {border-radius: 16px; border: 2px solid __border__; font-weight: 600; min-height: 3rem;}
 .stButton > button[kind="primary"] {background: __accent__; border: 0; color: #fff; font-size: 1.1rem; font-weight: 800;}
 .wordmark {font-weight: 800; font-size: 2.3rem; color: __head__; letter-spacing: -1px; line-height: 1;}
 .tagline {color: __accent__; font-weight: 600; margin-top: 2px;}
 .pill {display: inline-block; padding: 6px 16px; border-radius: 999px; font-weight: 700; background: #D9EDD9; color: #1F5B30; font-size: .95rem;}
 .banner {background: __banner__; border-radius: 22px; padding: 18px 24px; display: flex; align-items: center; gap: 22px; flex-wrap: wrap;}
 .banner h2 {margin: 0; font-size: 1.6rem;} .banner .big {font-size: 2rem; font-weight: 800; color: __head__; margin-top: 6px;}
 .bubble {background: __banner__; border-radius: 20px; padding: 14px 20px; font-size: 1.05rem; border: 2px solid __border__; position: relative;}
 .bubble:before {content: ""; position: absolute; left: -14px; top: 26px; border: 8px solid transparent; border-right-color: __banner__; border-left: 0;}
 .bob {animation: bob 3s ease-in-out infinite;}
 @keyframes bob {0%,100% {transform: translateY(0);} 50% {transform: translateY(-6px);}}
 .chip {display: inline-block; padding: 5px 14px; border-radius: 999px; font-weight: 700; margin: 2px 4px 2px 0; font-size: .92rem;}
 .chip.good {background: #D5ECD7; color: #1F5B30;} .chip.warn {background: #FBE7C0; color: #7A5200;} .chip.high {background: #F6D5CC; color: #8A3A28;}
 .meter {height: 14px; border-radius: 999px; background: #E6E9E3; overflow: hidden; margin: 6px 0 2px;}
 .meter .fill {height: 100%; border-radius: 999px;}
 .badge {display: inline-block; width: 46%; margin: 4px 1%; padding: 10px 6px; border-radius: 16px; text-align: center; background: __sand__; border: 2px solid __border__; font-size: .92rem; vertical-align: top;}
 .badge.locked {opacity: .45; filter: grayscale(1);} .badge .em {font-size: 2rem; display: block;}
 .status {border-radius: 16px; padding: 14px 18px; font-size: 1.1rem; font-weight: 600; margin: 8px 0;}
 .status.green {background: #D5ECD7; color: #1F5B30;} .status.amber {background: #FBE7C0; color: #7A5200;} .status.red {background: #F6D5CC; color: #8A3A28;}
 .tip {background: __banner__; border-radius: 16px; padding: 12px 16px;}
 .jcard {border: 2px solid __border__; border-radius: 16px; padding: 10px 14px; margin: 6px 0; background: __card__;}
 .jcard .d {color: #77857A; font-size: .85rem;}
 .garden {display: flex; flex-wrap: wrap; gap: 10px; background: linear-gradient(#E9F1E3 60%, #CBB38A 60%); border-radius: 20px; padding: 16px; justify-content: center;}
 .plot {text-align: center; width: 78px;} .plot .pl {font-size: 2.6rem; animation: pop .7s ease both;} .plot small {display: block; font-size: .7rem; color: #3B2F1B;}
 .plot.empty .pl {opacity: .25; filter: grayscale(1); animation: none;}
 @keyframes pop {0% {transform: scale(0);} 70% {transform: scale(1.25);} 100% {transform: scale(1);}}
 .note {font-size: .9rem; color: #5B6B5F;}
 .stApp [data-testid="stMainBlockContainer"] {animation: fadein .5s ease both;}
 @keyframes fadein {from {opacity: 0; transform: translateY(8px);} to {opacity: 1; transform: none;}}
 .stButton > button {transition: transform .18s ease, box-shadow .18s ease, background .18s ease;}
 .stButton > button:hover {transform: translateY(-4px); box-shadow: 0 8px 18px rgba(47,93,62,.22); border-color: __accent__;}
 .stButton > button:active {transform: translateY(0) scale(.97);}
 div[data-testid="stVerticalBlockBorderWrapper"] {transition: box-shadow .25s ease, transform .25s ease;}
 div[data-testid="stVerticalBlockBorderWrapper"]:hover {box-shadow: 0 10px 26px rgba(47,93,62,.12);}
 div[data-testid="stMetric"] {transition: transform .2s ease;} div[data-testid="stMetric"]:hover {transform: scale(1.03);}
 .badge {transition: transform .2s ease;} .badge:not(.locked):hover {transform: rotate(-3deg) scale(1.07);}
 .plot .pl {display: inline-block; cursor: default; transition: transform .2s;} .plot:not(.empty) .pl:hover {animation: sway2 .6s ease-in-out;}
 @keyframes sway2 {0%,100% {transform: rotate(0);} 25% {transform: rotate(-12deg) scale(1.15);} 75% {transform: rotate(12deg) scale(1.15);}}
 .jcard {transition: transform .18s ease, box-shadow .18s ease;} .jcard:hover {transform: translateX(4px); box-shadow: 0 4px 12px rgba(47,93,62,.15);}
 .meter .fill {transition: width .6s ease;}
 @media (prefers-reduced-motion: reduce) {* {animation: none !important; transition: none !important;}}
</style>
"""
for key, value in T.items():
    CSS = CSS.replace(f"__{key}__", value)
st.markdown(CSS, unsafe_allow_html=True)

sym = data.CURRENCIES[S.currency]["symbol"]
to_usd_rate = data.CURRENCIES[S.currency]["to_usd"]

# ===========================================================================
# 4. SHARED CALCULATIONS (used by Pip's messages and by several pages)
# ===========================================================================
ym_now = (TODAY.year, TODAY.month)
summ_now = engine.monthly_summary(S.purchases, *ym_now, S.avoided)
status_now = engine.footprint_status(summ_now["total_co2"], S.goal) if summ_now["count"] else "green"

prev_ethical = engine.is_ethical_brand(S.in_brand, S.in_ethical)
prev_co2 = engine.calculate_impact(S.in_price, S.currency, S.in_type, prev_ethical)
prev_green = engine.is_green_choice(S.in_type, prev_ethical)
prev_swap, prev_saved = engine.swap_saving(S.in_price, S.currency, S.in_type, prev_ethical)


def pip_state_and_message():
    """Choose Pip's emotional state and what Pip says, from the app state."""
    ev = S.event
    if ev:
        if ev["kind"] == "error":
            return "learning", "Hmm, the price needs to be more than zero. Try again?"
        if ev.get("new_badges") or ev.get("new_goals"):
            return "goal", "LOOK AT US GROWING! \U0001F331 You just reached something new, check the confetti!"
        if ev["kind"] == "paused":
            return "excited", f"Mindful pause! You skipped about {ev['co2']} kg of CO\u2082e. That counts!"
        if ev["kind"] == "green":
            return "excited", f"One small choice, one happy planet! That {ev['type'].lower()} is only about {ev['co2']} kg CO\u2082e."
        extra = (f" Swapping to {ev['swap'].lower()} next time could save about {ev['saved']} kg. Totally optional!"
                 if ev["swap"] else "")
        return "learning", f"We're improving, not chasing perfection. Logged about {ev['co2']} kg CO\u2082e.{extra}"
    if S.page == LOG:
        if S.in_price > 0 and not prev_green:
            return "learning", "Wait! I found another option you might like. Peek at the greener swaps below."
        if S.in_price > 0:
            return "excited", "Ooh, that's a low-impact pick! Log it to watch our garden grow."
        return "learning", "Ooh! Let's check the impact of this one. Add a price to begin."
    if S.page == SWAPS:
        return "learning", "Wait! I found another option you might like. Pick a product and your budget."
    if not S.purchases:
        return "before", "Hey shopper! Shopping feels a bit confusing to me. Let's learn what our choices really cost, together?"
    if summ_now["count"] >= 3 and status_now == "green":
        return "goal", "We're thriving! This month's footprint is well within your goal."
    return "learning", "Ooh! Let's keep learning. Every purchase you log teaches me something new."


pip_state, pip_msg = pip_state_and_message()


CHATTER = data.PIP_CHATTER + data.ECO_TIPS + data.QUOTES


def pip_say(width=150):
    """Pip + speech bubble as a live web component: idle animation per mood, follows the
    pointer, hops and sparkles when tapped, types its message out and shares tips."""
    ev = S.event
    burst = bool(ev and (ev.get("new_badges") or ev.get("new_goals") or ev["kind"] in ("green", "paused")))
    components.html(pip_widget(pip_state, pip_msg, T, CHATTER, burst=burst, width=width, nonce=S.nonce,
                               font_size="1.2rem" if S.contrast else "1.02rem"), height=230)


def pct_text(value):
    return "n/a" if value is None else f"{value:+d}%"


def goal_rows(summ):
    """Render the personal eco goals as progress bars."""
    if not S.my_goals:
        st.caption("Pick some personal eco goals in the sidebar settings.")
    for g in S.my_goals:
        cur, tgt, done = engine.goal_progress(g, summ, S.goal)
        frac = 0.0 if not tgt else min(cur / tgt, 1.0)
        tick = "\u2705" if done else ""
        label = f"{data.GOALS[g]['emoji']} {data.GOALS[g]['name']}  {tick}"
        st.progress(frac, text=label)


def draw_for_state(summ):
    """Pick the turtle drawing that matches what just happened."""
    ev = S.event
    if ev and ev.get("new_badges"):
        return turtle_art.draw_badge(), "New badge: " + data.BADGES[ev["new_badges"][0]]["name"]
    if ev and ev["kind"] in ("green", "paused"):
        return turtle_art.draw_leaf(), "A leaf for your green choice!"
    if S.purchases:
        status = engine.footprint_status(summ["total_co2"], S.goal) if summ["count"] else "green"
        return turtle_art.draw_footprint_status(status), f"Your footprint this month: {status}"
    return turtle_art.draw_sprout(), "Log a purchase and Pip starts drawing!"


# ===========================================================================
# 5. HEADER + NAVIGATION
# ===========================================================================
h1, h2 = st.columns([3, 1.4], vertical_alignment="center")
with h1:
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px">{logo_img(52)}'
                f'<div><div class="wordmark">kindcart.</div>'
                f'<div class="tagline">Shop mindfully. Grow gently.</div></div></div>', unsafe_allow_html=True)
with h2:
    st.markdown(f'<div style="text-align:right"><span class="pill">{data.PIP_STATES[pip_state]["pill"]}</span>'
                f'<div class="note">A ShopImpact experience</div></div>', unsafe_allow_html=True)

st.radio("Navigate", PAGES, key="page", horizontal=True, label_visibility="collapsed", on_change=clear_event)

if S.event and (S.event.get("new_badges") or S.event.get("new_goals")) and not S.event.get("shown"):
    st.balloons()
    S.event["shown"] = True


# ===========================================================================
# 6. PAGES
# ===========================================================================
def page_home():
    pct = min(round(100 * summ_now["total_co2"] / S.goal), 100) if S.goal else 0
    st.markdown('<div class="banner"><div><h2>Hey, shopper!</h2>'
                '<div>Ready to make a little difference today?</div>'
                '<div class="big">Small choices. Bigger impact.</div></div></div>', unsafe_allow_html=True)
    pip_say(160)
    c1, c2, c3 = st.columns(3)
    c1.metric("\U0001F6CD\uFE0F Purchases logged", len(S.purchases))
    c2.metric("\U0001F33F Eco badges earned", len(S.earned))
    c3.metric("\u23F8\uFE0F CO\u2082 avoided by pausing", f"{sum(a['co2'] for a in S.avoided):.1f} kg")

    st.markdown("### Your monthly progress")
    st.progress(pct / 100, text=f"{pct}% of your {S.goal} kg CO\u2082 budget used this month")
    cmp_ = engine.compare_months(S.purchases, *ym_now)
    if cmp_["change_pct"] is not None:
        better = cmp_["change_pct"] <= 0
        arrow = "\U0001F4C9" if better else "\U0001F4C8"
        cheer = "Lovely, keep going!" if better else "No worries, small swaps add up."
        st.caption(f"{arrow} {pct_text(cmp_['change_pct'])} vs last month ({cmp_['prev_total']} kg). {cheer}")
    elif not S.purchases:
        st.caption("Log your first purchase, or load demo data from the sidebar, to see your progress.")

    st.markdown("### Explore your shopping world")
    a, b = st.columns(2)
    a.button("\u2795  Log a purchase", on_click=go, args=(LOG,), width="stretch")
    a.caption("Track your shopping")
    b.button("\U0001F4CA  My impact", on_click=go, args=(IMPACT,), width="stretch")
    b.caption("View your dashboard")
    a.button("\U0001F504  Green swaps", on_click=go, args=(SWAPS,), width="stretch")
    a.caption("Discover alternatives within your budget")
    b.button("\U0001F3C5  My achievements", on_click=go, args=(ACH,), width="stretch")
    b.caption("Collect your badges and grow your garden")

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("#### \U0001F3AF My personal eco goals")
            goal_rows(summ_now)
    with right:
        fact = data.ECO_TIPS[TODAY.toordinal() % len(data.ECO_TIPS)]
        st.markdown(f'<div class="tip"><b>\U0001F4A1 Eco fact of the day</b><br>{fact}</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<div class="tip" style="background:{T["sand"]}">\u201C{S.quote}\u201D</div>', unsafe_allow_html=True)
        st.button("\U0001F501 New quote", on_click=lambda: S.update(quote=random.choice(data.QUOTES)))


def page_log():
    pip_say(150)

    recent = engine.quick_add_items(S.purchases)
    if recent:
        st.markdown("**\u26A1 Quick add**  (tap to log again today)")
        cols = st.columns(len(recent))
        for i, item in enumerate(recent):
            cols[i].button(f"{data.PRODUCT_TYPES[item['type']]['icon']} {item['type']}\n{item['brand']} \u00B7 "
                           f"{data.CURRENCIES[item['currency']]['symbol']}{item['price']:g}",
                           key=f"qa{i}", on_click=quick_add, args=(i,), width="stretch")

    with st.container(border=True):
        st.subheader("\U0001F6D2 What are you planning to buy?")
        c1, c2, c3, c4 = st.columns([2.2, 2, 1.4, 1.4])
        c1.selectbox("Product type", list(data.PRODUCT_TYPES), key="in_type", on_change=on_type_change,
                     format_func=lambda k: f"{data.PRODUCT_TYPES[k]['icon']}  {k}")
        c2.text_input("Brand (optional)", key="in_brand", placeholder="e.g. Veja, Thrift, Local Market")
        c3.number_input(f"Price ({sym})", min_value=0.0, step=5.0, format="%.2f", key="in_price")
        c4.date_input("Purchase date", key="in_date")
        d1, d2 = st.columns([2, 3])
        d1.checkbox("Certified ethical brand (B Corp, Fair Trade...)", key="in_ethical")
        d2.text_input("Note (optional)", key="in_note", placeholder="e.g. birthday gift, needed for school")

    # ---- Impact Decoder + Impact Explained -------------------------------
    with st.container(border=True):
        st.subheader("\U0001F50D Impact decoder")
        m1, m2 = st.columns([1, 2], vertical_alignment="center")
        m1.metric("Estimated CO\u2082e", f"{prev_co2} kg")
        with m2:
            level = engine.impact_level(S.in_type)
            klass = {"Low": "good", "Medium": "warn", "High": "high"}[level]
            score = engine.impact_score(S.in_type)
            color = {"Low": "#6FBF7B", "Medium": "#E8B84B", "High": "#D98C7A"}[level]
            green_label = "\U0001F33F Green choice" if prev_green else "Not yet a green choice"
            green_klass = "good" if prev_green else "warn"
            st.markdown(f'<span class="chip {klass}">{level} impact item</span>'
                        f'<span class="chip {green_klass}">{green_label}</span>'
                        f'<div class="meter"><div class="fill" style="width:{max(score, 4)}%;background:{color}"></div></div>'
                        f'<div class="note">Impact meter: {score}/100</div>', unsafe_allow_html=True)
        eq = engine.explain_equivalents(prev_co2)
        st.write(f"\U0001F4A1 **In everyday terms (approx.):** like driving **{eq['km_driven']} km**, "
                 f"charging a phone **{eq['phone_charges']} times**, or what one tree absorbs in "
                 f"**{eq['tree_months']} months**.")
        if prev_swap:
            st.write(f"\U0001F331 Swap to **{prev_swap.lower()}** and save about **{prev_saved} kg**.")
        with st.expander("\U0001F50E Why this number? (transparency notes)"):
            for note in engine.explain_impact(S.in_price, S.currency, S.in_type, prev_ethical):
                st.markdown(f"- {note}")
            st.caption("kindcart. is a learning and awareness tool, not an official environmental certification.")
        with st.expander(f"\U0001F331 Greener ideas for {S.in_type.lower()}"):
            for alt in engine.greener_alternatives(S.in_type):
                st.markdown(f"**{alt['name']}**: {alt['why']}")

    # ---- Before You Buy ---------------------------------------------------
    with st.container(border=True):
        st.subheader("\U0001F914 Before you buy")
        st.caption("A gentle pause. There is no pressure to give up the purchase.")
        q1, q2 = st.columns(2)
        need = q1.radio("Do you need it right now?", ["Yes, I do", "It can wait"], key="bw_need", horizontal=True)
        reuse = q2.radio("Could you reuse, borrow or repair something?", ["Not really", "Maybe!"], key="bw_reuse", horizontal=True)
        if need == "It can wait" or reuse == "Maybe!":
            st.info(f"Pip thinks pausing is a great idea: you'd skip about {prev_co2} kg CO\u2082e and "
                    f"{sym}{S.in_price:,.0f}.")
        st.button("\u23F8\uFE0F Pause this purchase (count it as avoided)", on_click=pause_purchase)

    st.button("\u2795 Log purchase", type="primary", on_click=log_purchase, width="stretch")

    ev = S.event
    if ev and ev["kind"] in ("green", "regular", "paused"):
        with st.container(border=True):
            r1, r2 = st.columns([2, 1])
            with r1:
                st.subheader("\U0001F389 Nicely done!")
                st.write(pip_msg)
                st.markdown(f'<div class="tip">\U0001F4A1 <b>Eco tip:</b> {S.tip}</div>', unsafe_allow_html=True)
                for g in ev.get("new_goals", []):
                    st.success(f"Goal reached: {data.GOALS[g]['name']}")
                for b in ev.get("new_badges", []):
                    st.success(f"New badge: {data.BADGES[b]['emoji']} {data.BADGES[b]['name']}")
            with r2:
                art, caption = draw_for_state(summ_now)
                components.html(art.to_html(caption=caption, nonce=S.nonce), height=360)


def page_impact():
    pip_say(130)
    months = sorted({(p["date"].year, p["date"].month) for p in S.purchases} | {ym_now}, reverse=True)
    if S.view_month not in months:
        S.view_month = ym_now
    centre, side = st.columns([2.3, 1])
    with centre:
        with st.container(border=True):
            st.subheader("\U0001F4CA Monthly dashboard")
            view = st.selectbox("Month", months, key="view_month",
                                format_func=lambda ym: date(ym[0], ym[1], 1).strftime("%B %Y"))
            summ = engine.monthly_summary(S.purchases, *view, S.avoided)
            spend_local = summ["total_spend_usd"] / to_usd_rate
            cmp_ = engine.compare_months(S.purchases, *view)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total spend", f"{sym}{spend_local:,.0f}")
            m2.metric("Total CO\u2082e", f"{summ['total_co2']} kg",
                      delta=pct_text(cmp_["change_pct"]) if cmp_["change_pct"] is not None else None,
                      delta_color="inverse", help="Change compared with the previous month.")
            m3.metric("Green choices", f"{summ['green_share']}%")
            m4.metric("Avoided by pausing", f"{summ['avoided_co2']} kg")

            if summ["count"] == 0:
                st.markdown('<div class="status amber">\U0001F331 Nothing logged for this month yet. '
                            'Log a purchase or load the demo data from the sidebar!</div>', unsafe_allow_html=True)
            else:
                status = engine.footprint_status(summ["total_co2"], S.goal)
                words = {"green": "\U0001F33F You're well within your goal. Lovely!",
                         "amber": "\U0001F324\uFE0F Close to your goal. A swap or two will help.",
                         "red": "\U0001F326\uFE0F Over your goal this month. No worries, small swaps add up."}
                st.markdown(f'<div class="status {status}">{words[status]}</div>', unsafe_allow_html=True)
                st.progress(min(summ["total_co2"] / S.goal, 1.0), text=f"{summ['total_co2']} of {S.goal} kg goal used")
                if cmp_["change_pct"] is not None:
                    st.caption(f"Last month: {cmp_['prev_total']} kg over {cmp_['prev_count']} purchases "
                               f"({pct_text(cmp_['change_pct'])} now).")

                t1, t2, t3 = st.tabs(["By category", "Monthly trend", "Shopping journal"])
                with t1:
                    cat = pd.Series(summ["by_category"], name="kg CO\u2082e").sort_values(ascending=False)
                    st.bar_chart(cat, color="#6F9E7B", horizontal=True)
                with t2:
                    frame = pd.DataFrame(S.purchases)
                    frame["month"] = pd.to_datetime(frame["date"]).dt.to_period("M").astype(str)
                    st.bar_chart(frame.groupby("month")["co2"].sum().rename("kg CO\u2082e"), color="#8EC5DA")
                with t3:
                    items = sorted(engine.purchases_in_month(S.purchases, *view), key=lambda p: p["date"], reverse=True)
                    for p in items:
                        chip = '<span class="chip good">green</span>' if p["green"] else '<span class="chip warn">higher impact</span>'
                        note = f' \u00B7 <i>{p["note"]}</i>' if p.get("note") else ""
                        st.markdown(
                            f'<div class="jcard"><span class="d">{p["date"].strftime("%d %b %Y")}</span><br>'
                            f'<b>{data.PRODUCT_TYPES[p["type"]]["icon"]} {p["type"]}</b> \u00B7 {p["brand"]} \u00B7 '
                            f'{data.CURRENCIES[p["currency"]]["symbol"]}{p["price"]:g} \u00B7 '
                            f'<b>{p["co2"]} kg</b> {chip}{note}</div>', unsafe_allow_html=True)
    with side:
        with st.container(border=True):
            st.subheader("\U0001F3AF My goals")
            goal_rows(engine.monthly_summary(S.purchases, *S.view_month, S.avoided))
        with st.container(border=True):
            st.subheader("\U0001F422 Pip draws (turtle)")
            art, caption = draw_for_state(engine.monthly_summary(S.purchases, *S.view_month, S.avoided))
            components.html(art.to_html(caption=caption, nonce=S.nonce), height=360)


def page_swaps():
    pip_say(130)
    with st.container(border=True):
        st.subheader("\U0001F504 Green within my budget")
        st.caption("Greener doesn't have to mean pricier. Costs are illustrative typical prices.")
        c1, c2, c3 = st.columns([2.2, 1.3, 1.3])
        c1.selectbox("What were you going to buy?", list(data.PRODUCT_TYPES), key="sw_type",
                     format_func=lambda k: f"{data.PRODUCT_TYPES[k]['icon']}  {k}")
        c2.number_input(f"Usual price ({sym})", min_value=1.0, step=5.0, format="%.2f", key="sw_price")
        c3.number_input(f"My budget ({sym})", min_value=1.0, step=5.0, format="%.2f", key="sw_budget")
        swaps = engine.budget_swaps(S.sw_price, S.sw_budget, S.currency, S.sw_type)
        if not swaps:
            st.success("This is already one of the greenest choices. Keep it up! \U0001F331")
        for i, sw in enumerate(swaps):
            info = data.PRODUCT_TYPES[sw["type"]]
            fit = ('<span class="chip good">\u2705 fits your budget</span>' if sw["fits"]
                   else '<span class="chip warn">\U0001F4B8 a little over budget</span>')
            eq = engine.explain_equivalents(sw["saved"])
            a, b = st.columns([4, 1.4], vertical_alignment="center")
            a.markdown(f'<div class="jcard"><b>{info["icon"]} {sw["type"]}</b><br>about {sym}{sw["est_cost"]:,.0f} '
                       f'\u00B7 saves about <b>{sw["saved"]} kg</b> (\u2248 {eq["km_driven"]} km driving)<br>{fit}</div>',
                       unsafe_allow_html=True)
            b.button("Use this swap", key=f"us{i}", on_click=use_swap, args=(sw["type"], sw["est_cost"]), width="stretch")
        st.markdown("**Other ideas**")
        for alt in engine.greener_alternatives(S.sw_type):
            st.markdown(f"- **{alt['name']}**: {alt['why']}")
        st.caption("Brand names are examples only. Always check a brand's own sustainability claims.")


def page_achievements():
    pip_say(150)
    a, b = st.columns([1, 1])
    with a:
        with st.container(border=True):
            st.subheader("\U0001F3C5 My badges")
            cards = ""
            for bid, info in data.BADGES.items():
                if bid in S.earned:
                    cards += f'<div class="badge"><span class="em">{info["emoji"]}</span><b>{info["name"]}</b></div>'
                else:
                    cards += (f'<div class="badge locked"><span class="em">\U0001F512</span>{info["name"]}'
                              f'<br><small>{info["how"]}</small></div>')
            st.markdown(cards, unsafe_allow_html=True)
    with b:
        with st.container(border=True):
            st.subheader("\U0001F331 My virtual garden")
            plots = ""
            for i, (bid, info) in enumerate(data.BADGES.items()):
                plant = data.GARDEN_PLANTS[i]
                if bid in S.earned:
                    plots += (f'<div class="plot"><div class="pl" style="animation-delay:{i * 0.12:.2f}s">{plant}</div>'
                              f'<small>{info["name"]}</small></div>')
                else:
                    plots += '<div class="plot empty"><div class="pl">\U0001F331</div><small>waiting...</small></div>'
            st.markdown(f'<div class="garden">{plots}</div>', unsafe_allow_html=True)
            st.caption(f"{len(S.earned)} of {len(data.BADGES)} plants grown. Every badge you earn plants something new.")
    c, d = st.columns([1, 1])
    with c:
        with st.container(border=True):
            st.subheader("\U0001F3AF My personal eco goals")
            goal_rows(engine.monthly_summary(S.purchases, *ym_now, S.avoided))
    with d:
        with st.container(border=True):
            st.subheader("\U0001F422 Pip draws (turtle)")
            art, caption = draw_for_state(summ_now)
            components.html(art.to_html(caption=caption, nonce=S.nonce), height=360)


{HOME: page_home, LOG: page_log, IMPACT: page_impact, SWAPS: page_swaps, ACH: page_achievements}[S.page]()

st.caption("CO\u2082 values are illustrative estimates for learning and awareness, not a certified carbon audit.")
