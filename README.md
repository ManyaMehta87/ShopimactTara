# 🌱 kindcart. · a ShopImpact experience

> **Shop mindfully. Grow gently.**
> At the shelf, a price tag shows one number. The planet's number is missing. **kindcart.** adds a second price tag, the estimated CO₂, *before* you pay, and a friendly sprout named **Pip** helps you choose greener, without guilt.

**🔗 Live app:** `PASTE YOUR STREAMLIT CLOUD LINK HERE`

| | |
|---|---|
| **Student** | `Your full name` |
| **Candidate registration number** | `Your registration number` |
| **CRS** | Artificial Intelligence |
| **Course** | Python Programming (Summative Assessment, Scenario 1) |
| **School** | `Your school name` |

![kindcart home screen](docs/screenshot-home.png)
*(Add screenshots to `docs/`: home, log a purchase with the impact decoder, impact dashboard, achievements with garden, a turtle drawing.)*

---

## 1. Project overview

**The problem.** Sellers know the supply chain behind a product; shoppers see only a price. This *information asymmetry* leaves well-meaning people guessing, and guilt-heavy carbon calculators make them feel judged. kindcart. closes the gap **at the moment of decision**.

**Who it is for.** Students, young adults and families who are curious about their footprint and on real budgets.

**How it feels.** Awareness, empowerment and fun, never guilt: soft sage and cream colours, live numbers, a mascot who reacts to you, badges that grow a virtual garden, and turtle drawings that appear stroke by stroke.

Full design thinking (personas, stakeholders, wireframes, palette, logic rules, tests, survey, ethics) is in [`docs/DESIGN.md`](docs/DESIGN.md).

## 2. Meet Pip

Pip is **alive in the browser**, not just a picture:
- a different idle animation for each mood (sway, wave, hop, proud pulse)
- Pip's head **tilts to follow your mouse or finger**
- **tap or hover**: Pip hops, sparkles pop out and Pip says something new
- Pip's speech is **typed out letter by letter**, and every ~20 seconds Pip shares a random eco tip
- celebrations burst with sparkles when you make a green choice, pause a purchase or earn a badge
- the turtle drawings are drawn by a **little walking turtle**, and you can **tap a drawing to replay it**
- cards, buttons, badges, garden plants and journal entries react when you hover over them

Pip has four emotional states that change with what you do:

| State | When |
|---|---|
| Curious (droopy) | Before you have learned or logged anything |
| Learning (waving) | While exploring impacts and swaps, or after a higher-impact purchase |
| Excited | After an eco-friendly choice or a mindful pause |
| Thriving (gardener) | After reaching a goal, earning a badge, or a month well within your goal |

## 3. Key features

**Compulsory**
- Inputs for product type, price and brand
- **Real-time CO₂ estimate** that updates as you type, before you log
- **Monthly dashboard**: spend, CO₂, green share, charts by category and by month, journal
- **8 badges**, including *Eco Saver of the Month* and *Low Impact Shopper*
- **Greener alternatives** for all 18 product types
- **Turtle graphics** (leaf, medal, footprint, sprout) drawn stroke by stroke

**Solutions to real shopper problems**
- **Impact Decoder + Impact Explained**: impact level, 0 to 100 meter, and equivalents (km driven, phone charges, tree-months)
- **Transparency Notes**: "Why this number?" shows the formula and says the figure is an estimate
- **Green Within My Budget**: estimated cost of each swap and a "fits your budget" flag (green can cost more, and the app says so)
- **Before You Buy**: a gentle pause; paused purchases count as CO₂ avoided and earn *Mindful Pause*
- **Quick Add**: typical prices as defaults and one-tap re-log of recent items
- **Shopping Journal** with notes, **Monthly Progress** versus last month, **Personal Eco Goals**
- **Virtual garden**: every badge you earn grows a plant
- Eco fact of the day, quotes, **high-contrast mode**, currency selector, CSV import/export, demo data

## 4. How it works

```
CO2e (kg) = price x (currency -> USD rate) x product multiplier   [x 0.85 if ethical brand]
```

`purchases` is a **list of dictionaries**; multipliers, alternatives, goals and badges are **dictionaries**; badge and goal rules are **functions**; the app uses loops, conditionals, `datetime` and `pandas.groupby`. Multipliers are **illustrative estimates**, not a certified carbon audit.

## 5. Files

| File | Role |
|---|---|
| `app.py` | Streamlit interface: 5 pages, navigation, widgets, session state, styling |
| `engine.py` | Pure-Python logic (no Streamlit): impact, summaries, badges, goals, budget swaps, comparisons |
| `data.py` | Curated data: multipliers, prices, alternatives, badges, goals, tips, currencies |
| `mascot.py` | Loads Pip's four images and builds Pip's live web component (HTML, CSS, JavaScript) |
| `turtle_art.py` | Turtle-style SVG engine and the eco drawings |
| `assets/` | `pip_before.png`, `pip_learning.png`, `pip_excited.png`, `pip_goal.png`, `logo.png` |
| `tests/test_engine.py` | 32 unit tests |
| `.streamlit/config.toml` | Colour theme |
| `requirements.txt` | `streamlit`, `pandas` |

**Why an "SVG turtle"?** Python's built-in `turtle` needs a desktop window (Tk), which cloud servers lack. `turtle_art.py` reproduces the same commands (`forward`, `left`, `penup`, `goto`, `circle`, `begin_fill`...) and plays the drawing back as an animation in the browser.

## 6. Run locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
streamlit run app.py
python -m unittest discover tests -v
```

## 7. Deployment (Streamlit Community Cloud)

1. Push **all** files and folders (including `assets/` and `.streamlit/`) to your public GitHub repo, with `app.py` at the top level.
2. On [share.streamlit.io](https://share.streamlit.io) choose *Create app*, pick the repo, branch `main`, main file `app.py`, then **Deploy**.
3. After any later change, commit and push to GitHub; Streamlit redeploys automatically (or use *Reboot app* from the app menu).
4. Share the repo with **ai.assignments@wacpinternational.org** (Settings → Collaborators) and paste the live URL at the top of this README.

## 8. Try it in 60 seconds

1. Open the sidebar and click **Load demo data**.
2. Watch Pip, the progress bar, badges and garden respond.
3. Go to **Log a purchase**, choose *Fast-fashion clothing*, read the impact decoder, then tap **Pause this purchase** or log it.
4. Open **Green swaps** and lower your budget to see which swaps still fit.
5. Switch on **High-contrast mode**.

## 9. Testing and feedback

32 automated tests (all passing), a 15-purchase manual script, a stakeholder survey summary and a user-feedback log are documented in [`docs/DESIGN.md`](docs/DESIGN.md).

## 10. Ethics and limitations

Estimates, not audits · gentle, guilt-free tone · self-declared "ethical" brands can be greenwashing, so verify · no login, no tracking, no personal data stored · brand names in suggestions are examples only · greener options favour ones that also save money, and the app is honest when green costs more.

## 11. Future improvements

Barcode scanning, a verified-brand database, per-item lifetime estimates, saved accounts with consent, sharing badges.
