# kindcart. (a ShopImpact experience): Design Document (Stages 1 to 4)

## 1. Problem statement

> **At the shelf, a price tag shows one number. The planet's number is missing.**
>
> A shopper can compare two jumpers by price, brand and colour in seconds, yet cannot see that one carries roughly six times the carbon footprint of the other. The seller knows the supply chain, the buyer sees only the price. This **information asymmetry** means that even people who *want* to shop greener are guessing, and guilt-heavy carbon calculators make them feel judged rather than helped.
>
> **kindcart.** (the friendly product identity of ShopImpact) closes that gap *at the moment of decision*. Before the shopper pays, the app attaches a second price tag, the estimated CO₂e, shows what a greener swap would save, and rewards good choices with badges, a growing virtual garden and a friendly sprout guide named **Pip**. The goal is awareness, empowerment and fun, never guilt.

**Goal:** help everyday shoppers see the hidden environmental cost of what they buy and gently motivate them to choose greener options.

## 2. Users and their needs

| Persona | Who | Pain point | What they need |
|---|---|---|---|
| Maya, 19, student | Tight budget, curious, loves thrift | Doesn't know whether her choices matter | Quick numbers, proof that second-hand wins, shareable badges |
| The Rao family | Parents + 2 kids, weekly grocery and home shopping | Overwhelmed by "eco" labels | Simple monthly totals, a clear goal, kid-friendly visuals |
| Sam, 27, young professional | Buys electronics and clothes online | Greenwashing fatigue | Honest comparisons (new vs refurbished), no lecture |

**Empathy map (summary)**
- *Thinks:* "I'd like to help the planet but I don't know what actually matters."
- *Feels:* guilty, confused, sometimes powerless.
- *Says:* "Is this brand actually green?"
- *Does:* decides in seconds, mostly on price.
- **Target emotions for the app:** awareness, empowerment, fun.

**Design principles:** (1) show the number *before* the purchase, (2) always offer a swap, never a scolding, (3) celebrate small wins, (4) large, readable type for everyone.

## 3. Stakeholders and the problems they face

| Stakeholder | Possible problem | Our response |
|---|---|---|
| Shoppers | Confusing data and too many inputs | Simple interface, defaults, plain-language explanations |
| Students | Limited budgets | Green Within My Budget shows cost-aware alternatives |
| Families | Different shopping needs | Flexible categories, shopping journal, personal goals |
| Ethical brands | Unsupported or incorrect claims | Transparency notes; ethical status is clearly labelled as self-declared |
| Retailers | Brands may be unfairly classified | Every estimate explains its basis; brand names in suggestions are examples only |
| App developers | Wrong calculations or missing data | Input validation, modular code, 32 unit tests |
| Environment-conscious organisations | Misleading environmental claims | Assumptions and limitations shown on screen and in the README |

**User problems and our solutions**

| Problem shoppers face | Feature |
|---|---|
| Don't know which products have higher impact | **Impact Decoder**: instant estimate, impact level and 0 to 100 meter |
| Don't understand carbon numbers | **Impact Explained**: km driven, phone charges, tree-months |
| Don't know greener options | **Green swaps** with "use this swap" |
| Green seems expensive | **Green Within My Budget**: estimated cost and "fits your budget" flag |
| Forget what they bought | **Shopping Journal** (dated cards with notes) |
| Can't tell if they are improving | **Monthly Progress**: this month vs last month |
| Feel guilty | **No-Guilt Feedback** from Pip |
| Don't trust sustainability claims | **Transparency Notes**: "why this number?", estimated vs self-declared |
| Logging is tedious | **Quick Add**: typical prices as defaults and one-tap re-log of recent items |
| Don't know where to begin | **Personal Eco Goals** and **Before You Buy** pause |

## 3b. Feature plan

| Must-have (compulsory) | Creative extras (all built) |
|---|---|
| Input fields: product type, price, brand | Pip the mascot with 4 emotional states and speech bubble |
| Real-time CO₂ estimate (live preview) | Home screen with explore cards and monthly progress |
| Monthly dashboard: spend, CO₂, charts | Before You Buy pause (CO₂ avoided is tracked) |
| 8 badges incl. Eco Saver and Low Impact Shopper | Virtual garden: each badge grows a plant |
| Greener-alternatives list for every product type | Personal eco goals, eco fact of the day, quotes |
| Turtle graphics on eco-friendly choices | High-contrast mode, currency selector, CSV import/export, demo data |

## 4. Visual style and mascot

**Brand:** *kindcart.* with the tagline "Shop mindfully. Grow gently." and a cart-and-sprout logo.
**Palette (soft sage and cream):** cream `#FBFBF8` (background), sage `#6F9E7B` (primary), forest `#2F5D3E` (headings and wordmark), pale green `#E9F1E3` (banners, bubbles), light grey-green `#F3F4F1` (stat cards), sand `#F5EFD8` (badges and quotes).
**Why:** greens signal nature and calm, cream keeps contrast gentle, and the traffic-light chips are softened so "over goal" never feels like an alarm.
**Typography:** Montserrat (fallback Segoe UI), 17 px base text (20 px in high-contrast mode), large metric values.
**Motion design:** Pip tilts toward the pointer, hops and sparkles on tap or hover, types out its speech and shares an eco tip every ~20 seconds; the turtle drawing is traced by a walking turtle and can be replayed; buttons, cards, badges and garden plants lift or wiggle on hover; a `prefers-reduced-motion` rule switches animations off for users who need calm screens.

**Mascot, Pip the sprout, has four emotional states:**

| State | When it appears | Image |
|---|---|---|
| Curious (droopy) | Before the user has logged or learned anything | `pip_before.png` |
| Learning (waving) | Exploring impacts and swaps, or after a higher-impact purchase | `pip_learning.png` |
| Excited | After an eco-friendly choice or a mindful pause | `pip_excited.png` |
| Thriving (gardener) | After reaching a goal or earning a badge, or a month well within goal | `pip_goal.png` |

## 5. Wireframe (desktop)

```
+----------------------------------------------------------------------------------+
| [logo] kindcart.                                          ( Pip is happy pill )  |
| Shop mindfully. Grow gently.                                                     |
| ( Home | Log a purchase | My impact | Green swaps | My achievements )  <- top nav |
|----------------------------------------------------------------------------------|
| HOME                                                                             |
| +-- banner ------------------------------------------------------------------+   |
| | [Pip]  Hey, shopper!  Ready to make a little difference today?              |   |
| |        Small choices. Bigger impact.                                        |   |
| +-----------------------------------------------------------------------------+   |
| [ Pip says: ... ]                                                                |
| [12 Purchases logged] [3 Eco badges earned] [x kg avoided by pausing]            |
| Your monthly progress  [=========70%=====      ]   -12% vs last month            |
| Explore your shopping world                                                      |
| [ Log a purchase ] [ My impact ]                                                 |
| [ Green swaps    ] [ My achievements ]                                           |
| [ My personal eco goals ]            [ Eco fact of the day ] [ quote ]           |
|----------------------------------------------------------------------------------|
| LOG A PURCHASE:  Pip bubble | Quick add chips | Input card | Impact decoder      |
|   (meter, equivalents, why-this-number) | Before you buy | [Log purchase]          |
|   -> result card: message, tip, goal/badge notices, turtle drawing               |
| MY IMPACT:  month picker, 4 metrics, status bar, tabs (category, trend, journal) |
|   side: goals, turtle drawing                                                    |
| GREEN SWAPS: product, usual price, budget -> swap cards with [Use this swap]     |
| MY ACHIEVEMENTS: badge grid | virtual garden | goals | turtle drawing            |
+----------------------------------------------------------------------------------+
```

*(Add your hand-drawn or Canva wireframe photo to `docs/wireframe.png` as well, and reference it in the README.)*

**Mobile:** Streamlit stacks the columns vertically; the top navigation wraps onto two lines.

## 6. Python logic design (Stage 2)

**Files:** `data.py` (curated data), `engine.py` (pure logic), `turtle_art.py` (drawings), `mascot.py` (Pip images), `assets/` (mascot and logo), `app.py` (interface), `tests/` (unit tests).

**Data structures**
- `purchases`: a **list** of **dictionaries** `{date, type, brand, price, currency, ethical, second_life, green, co2}`
- `PRODUCT_TYPES`: a dict of dicts (multiplier, group, swap target, icon)
- `ALTERNATIVES`: dict mapping each type to a **list** of suggestions
- `BADGES` (display) and `BADGE_RULES` (functions) both keyed by badge id

**Calculation rules**
1. `CO₂e (kg) = price × currency→USD rate × product multiplier`
2. If the brand is ethical (ticked or on the curated list): `× 0.85`
3. A product is *eco-tier* if its multiplier ≤ 0.20 kg per USD; a purchase is a *green choice* if it is eco-tier **or** from an ethical brand.
4. Swap saving = footprint now − footprint of the type named in `swap_to`.
5. Equivalents: 0.21 kg CO₂ per km driven; one tree absorbs about 1.75 kg per month; one phone charge is about 0.008 kg (all approximate).
6. Impact level: Low ≤ 0.20, Medium ≤ 0.45, High above (kg per USD). Impact score = multiplier ÷ 0.90 × 100.
7. Green Within My Budget: alternative cost = usual price × (alternative price factor ÷ current price factor). Green alternatives can cost more (for example reusables upfront) and the app says so.
8. Monthly progress: change % = (this month − last month) ÷ last month × 100.
9. Paused purchase: CO₂ avoided = what the purchase would have cost in CO₂e.

**Badge rules (evaluated for the month of the latest purchase)**

| Badge | Rule |
|---|---|
| First Step | at least 1 purchase logged |
| Footprint Tracker | at least 10 purchases logged |
| Low Impact Shopper | ≥ 3 purchases and month CO₂ ≤ goal |
| Eco Saver of the Month | ≥ 5 purchases, CO₂ ≤ 50% of goal, ≥ 60% green choices |
| Ethical Brand Champion | ≥ 3 ethical-brand purchases in the month |
| Second-Life Hero | ≥ 2 second-hand / refurbished / refill purchases in the month |
| Green Streak | last 3 purchases were all green choices |
| Mindful Pause | paused at least 1 purchase with *Before you buy* in the month |

**Honesty note:** multipliers are illustrative spend-based estimates built to show *relative* differences between choices. They are not a certified life-cycle assessment.

## 7. Turtle graphics (Stage 3)

Python's `turtle` module draws in a desktop window and needs Tk, which a cloud server does not have. `turtle_art.py` therefore contains an **SVG turtle** with the same commands (`forward`, `left`, `right`, `penup`, `pendown`, `goto`, `circle`, `begin_fill`, `end_fill`). It records every move and plays it back as an animated SVG, so users watch the leaf, badge, footprint or sprout being drawn stroke by stroke.

| Moment | Drawing |
|---|---|
| Nothing logged yet | Sprout in a pot |
| Green choice logged | Leaf |
| New badge earned | Medal (plus balloons) |
| Otherwise | Footprint coloured by monthly status (green / amber / red) |

## 8. Testing (Stage 4)

### 8.1 Automated tests
`python -m unittest discover tests -v` runs 32 tests covering the formula, currency conversion, zero or negative prices, ethical-brand discount, swap savings, monthly totals, empty months, traffic-light status, every badge rule, impact levels, transparency notes, budget swaps (including when green costs more), month-on-month comparison, paused purchases, quick add and personal goals. **All 32 pass.**

### 8.2 Manual test script: 15 purchases (cheap, expensive, eco, non-eco)
Enter these in order (USD) and check the live preview matches the expected value before pressing *Log*.

| # | Product | Brand | Price ($) | Expected kg CO₂e | Green? |
|---|---|---|---|---|---|
| 1 | Fast-fashion clothing | QuickStyle | 45 | 22.5 | No |
| 2 | Second-hand clothing | Thrift (ethical) | 22 | 1.5 | Yes |
| 3 | Leather shoes | StepRight | 120 | 84.0 | No |
| 4 | Recycled-material shoes | Veja (ethical) | 60 | 12.75 | Yes |
| 5 | New electronics | TechNova | 520 | 234.0 | No |
| 6 | Refurbished electronics | ReNew | 80 | 12.0 | Yes |
| 7 | Meat & dairy groceries | Local Mart | 38 | 34.2 | No |
| 8 | Plant-based groceries | GreenBasket | 30 | 6.0 | Yes |
| 9 | Local seasonal produce | Farmers Market (ethical) | 18 | 1.84 | Yes |
| 10 | Packaged snacks | SnackCo | 12 | 4.2 | No |
| 11 | Single-use plastic goods | BulkPack | 9 | 5.4 | No |
| 12 | Reusable household goods | Local Market (ethical) | 15 | 1.27 | Yes |
| 13 | New furniture | FlatHome | 250 | 100.0 | No |
| 14 | Second-hand furniture | Thrift (ethical) | 60 | 3.57 | Yes |
| 15 | Refill / zero-waste cosmetics | The Body Shop (ethical) | 20 | 2.04 | Yes |

**Checks to tick off:** totals update immediately after each log, the progress bar and status change colour as the goal is crossed, *Green Streak* appears after three green choices in a row, *First Step* appears after purchase 1, *Footprint Tracker* after purchase 10, the leaf appears on green purchases and the medal on a new badge, prices of 0 show Tara's friendly error, *Undo last* and *Clear everything* work. Also check: choosing a product type fills a sensible default price, *Quick add* re-logs a recent item in one tap, *Pause this purchase* adds to "avoided" and awards *Mindful Pause*, *Green swaps* shows "fits your budget" flags and *Use this swap* pre-fills the Log page, the dashboard shows the change versus last month, Pip's picture changes (curious, learning, excited, thriving), and each badge grows a plant in the garden.

### 8.3 User feedback log (fill in with YOUR real testers)

| Tester | What confused them / what they said | Change I made |
|---|---|---|
| (name, e.g. friend) | | |
| (name, e.g. parent) | | |
| (name, e.g. sibling) | | |

*Tip: watch quietly while they use the app for two minutes without helping, and write down where they hesitate.*

## 8b. Stakeholder survey (add your real results)

| Question asked | Key finding | What I changed |
|---|---|---|
| (paste from your survey) | | |

*Summarise your survey in 3 to 5 rows: the question, the headline result (for example "68% said green products feel too expensive"), and the feature or wording you changed because of it.*

## 9. Ethical reflection

- **Accuracy and honesty:** CO₂ values are estimates. The app says so on screen and in the README, so it cannot mislead users into thinking it is a certified audit.
- **No guilt, no shaming:** language is encouraging; "over goal" messages stay gentle. Behaviour change lasts longer when it feels good.
- **Greenwashing risk:** ethical-brand status can be self-declared. The checkbox is a trust-based input, and the app asks users to verify claims themselves.
- **Fairness and access:** greener products are sometimes more expensive. The suggestions therefore favour second-hand, repair, refill and library options that save money too. High-contrast mode, large text and currency choice widen access.
- **Privacy:** no login, no tracking, no personal data. Purchases live only in the browser session unless the user downloads a CSV.
- **Societal impact:** the project turns an invisible externality into a visible number, which is the first step towards informed consumer choice. It cannot replace policy or industry change, and it says so.
