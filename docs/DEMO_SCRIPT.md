#  Z-Score Hackathon Demo Script

##  **Elevator Pitch (30 seconds)**
"Z-Score revolutionizes credit assessment for India's 190 million underbanked population using explainable AI and gamified financial journeys. We turn credit invisibility into creditworthiness."

##  **Demo Flow (4 minutes)**

### **Act 1: The Problem (30 seconds)**
- "Meet Sarah, a freelancer with no traditional credit history"
- "Banks reject her loan application - she's credit invisible"
- Show traditional banking rejection scenario

#  Z-Score Hackathon Demo Script

##  Elevator pitch (30 seconds)
"Z-Score revolutionizes credit assessment for India's 190 million underbanked population using explainable AI and gamified financial journeys. We turn credit invisibility into creditworthiness."

##  Demo flow (4 minutes)

### Act 1 — The problem (30 seconds)
- "Meet Sarah, a freelancer with no traditional credit history."
- "Banks reject her loan application — she's credit invisible."
- Visual: short slide showing rejection + stat about credit invisibility.
#  Z-Score Hackathon Demo Script

##  Elevator pitch (30 seconds)

"Z-Score revolutionizes credit assessment for India's 190 million underbanked population using explainable AI and gamified financial journeys. We turn credit invisibility into creditworthiness."

##  Demo flow (4 minutes)

### Act 1 — The problem (30 seconds)

- "Meet Sarah, a freelancer with no traditional credit history."
- "Banks reject her loan application — she's credit invisible."
- Visual: short slide showing rejection + stat about credit invisibility.

### Act 2 — Z-Score solution (2.5 minutes)

#  Z-Score Hackathon Demo Script

##  Elevator pitch (30 seconds)

"Z-Score revolutionizes credit assessment for India's 190 million underbanked population using explainable AI and gamified financial journeys. We turn credit invisibility into creditworthiness."

##  Demo flow (4 minutes)

### Act 1 — The problem (30 seconds)

- "Meet Sarah, a freelancer with no traditional credit history."
- "Banks reject her loan application — she's credit invisible."
- Visual: short slide showing rejection + stat about credit invisibility.

### Act 2 — Z-Score solution (2.5 minutes)

User journey demo

1. Quick onboarding (20s)

   - Show streamlined signup and emphasize minimal data & privacy.

2. Trust score assessment (45s)

   - Generate a live trust score for demo user (Sarah).
   - Show SHAP explanation and say: "Here's exactly why the score is X and how to improve it." Point to the top 3 drivers.

3. Gamified improvement (35s)

   - Trigger a mission (e.g., pay a bill), show Z-credits and trust bar animation.
   - Narrate: "Small guided steps that move behavior and score."

4. Explainable AI dashboard (30s)

   - Show factor importance, recommendations, and transparent decision insights.

### Act 3 — Admin & business impact (45s)

- Switch to admin dashboard and show population-level uplift, inclusion metric, and model performance (AUC/precision).
- Script example: "Pilot results: +20% approvals among previously invisible users while default rate was maintained." (Replace with real pilot numbers if available.)

### Act 4 — Tech credibility & ask (45s)

- Say: "Built on XGBoost + logistic regression ensemble, SHAP for interpretability, Streamlit for demo, and a production-ready pipeline."
- Close: "We’re seeking pilot partners and early customers to scale — join us."

## Short narrator cheat-sheet (one-liners)

- Opening: "We turn credit invisibility into creditworthiness — with transparency and simple actions."
- SHAP: "This chart explains exactly why the score is what it is and how to improve it."
- Gamification: "Missions create small habit wins that move the score and the user's life."
- Close: "Transparent models, measurable inclusion — that's Z-Score."

## Demo environment — exact run steps (macOS / zsh)

Make sure your virtualenv is active and dependencies are installed.

1) Activate your venv (if present):

```bash
source .venv/bin/activate
```

2) Install (if needed):

```bash
pip install -r requirements.txt
```

3) Launch options (preferred: `start.sh`):

```bash
./start.sh --app=user    # user app → http://localhost:8502
./start.sh --app=admin   # admin app → http://localhost:8503
```

Or run directly:

```bash
streamlit run src/apps/app.py --server.port 8501   # main launcher UI
streamlit run src/apps/app_user.py --server.port 8502
streamlit run src/apps/app_admin.py --server.port 8503
```

Quick verification before you present:

- Visit `http://localhost:8502` and log in as `demo_user` (UI shows demo credentials).
- Visit `http://localhost:8503` for the admin overview.

If a port is in use, run with `--server.port <alt-port>` and update the URL in your slides.

## Pre-demo checklist

- [ ] `.venv` activated and dependencies installed
- [ ] `./start.sh --app=user` opens `http://localhost:8502`
- [ ] `./start.sh --app=admin` opens `http://localhost:8503`
- [ ] Sample profiles loaded (Sarah, Raj, Priya)
- [ ] SHAP visuals render in the Explain panel
- [ ] Recording/screenshots ready as backup

## Backup plan (when live fails)

- Have screenshots of onboarding, SHAP waterfall, trust bar and mission completion.
- Have a 2-minute recorded demo ready to play.
- If Streamlit stalls, switch to slides and narrate the demo while showing screenshots.

## Judge Q&A (short crisp answers)

- "How is this different from CIBIL?" → "CIBIL records credit history; we create transparent, actionable credit signals for the credit-invisible using behavioral and alternative data, explained with SHAP."
- "Business model?" → "B2B2C: subscription + per-evaluation pricing for lenders, plus analytics for risk teams."
- "Data privacy?" → "Minimal data collection, opt-in flows, and DPDPA-aware controls."
- "Go-to-market?" → "Pilot with MFIs and NBFCs, followed by integrations with digital lenders and fintechs."
- "Model accuracy?" → "Validated on held-out data; thresholds tuned with partners to balance inclusion and risk (example pilot: +20% approvals among previously invisible users)."

## Presentation tips — delivery and visuals

- Use the first 30s to make judges care about the human story.
- Show SHAP and walk through 2–3 concrete recommendations.
- Demonstrate one mission live — judges like tangible behavior change.
- Keep technical depth to a single backup slide unless asked.

## Final notes

- Keep to 4 minutes. Practice transitions (user → admin → ask) so tab switching is smooth.
- Want a 2-slide "judge cheat sheet" with URLs and run commands? I can add `docs/JUDGE_CHEATSHEET.md` to the repo.
