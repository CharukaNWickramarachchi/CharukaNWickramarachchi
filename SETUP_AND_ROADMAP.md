# Setup Guide

## 1. Add the files
Your profile repo must be named **exactly** `CharukaNWickramarachchi/CharukaNWickramarachchi`
(you said you've already created it). Copy everything in this folder into it,
preserving the paths:

```
README.md
assets/digital_dna.svg
assets/tech_constellation.svg
.github/workflows/update-readme.yml
.github/workflows/snake.yml
.github/scripts/generate_stats.py
```

```bash
git add .
git commit -m "Add Charuka OS animated profile"
git push
```

## 2. Enable the automation
1. **Settings → Actions → General → Workflow permissions** → set to
   **"Read and write permissions"**. Save.
2. Go to the **Actions** tab → run **"Update Live Intelligence"** manually once
   (Run workflow button). This fills in the Live Pulse table and regenerates
   `assets/digital_dna.svg` with your real repo/language data. It then repeats
   automatically every day.
3. Run **"Generate Snake Animation"** manually once too. It creates an `output`
   branch with the snake SVG the README already links to.

## 3. Fill in the real content
The README ships with **honest placeholders**, not fake data:
- `assets/digital_dna.svg` — placeholder until step 2 runs for real.
- **Live Development Pulse** table — says "syncing..." until step 2 runs.
- **Project Intelligence** cards — `*(fill in)*` markers for your actual project
  details (Premier League Analytics Pro, CardioVision AI, Fashion Retail,
  Hospital system). Replace those with real numbers/tech/status.
- **Connect** section — swap in your real LinkedIn/email/Twitter/Medium.

Never fabricate numbers here (fake star counts, fake "Development Index"
scores) — a technical reviewer who checks your repos against inflated claims
on the README is a worse outcome than a modest, accurate profile.

## 4. What's genuinely possible in a README (built above)
✅ Terminal boot + typing animations
✅ Live badges / status
✅ Auto-updating stats pulled from the real GitHub API (not static)
✅ Digital DNA chart computed from your actual language usage
✅ Contribution snake, stats cards, streak, trophies, activity graph
✅ Tech constellation diagram
✅ Collapsible project/experiment cards
✅ Daily automated regeneration via GitHub Actions

## 5. What needs a separate hosted web app (not a README)
GitHub READMEs render static Markdown/SVG only — no JavaScript execution, no
click handlers, no chatbot, no live database. These layers from your blueprint
are real engineering projects in their own right:

| Feature | Why it needs a real app |
|---|---|
| **Ask Charuka (AI assistant)** | Needs a backend calling an LLM API — can't run in a README |
| **Knowledge Graph** (click a skill, see linked projects) | Needs client-side JS + interactivity |
| **Digital City visualization** | Needs a rendering engine (Canvas/WebGL) and interaction |
| **XP / Level system tied to real milestones** | Needs a database to track state over time |
| **Full portfolio site** (charuka.dev) | Needs hosting, routing, a real frontend framework |

**Recommended path:** build that as a separate Next.js (or similar) app,
deployed free on Vercel/Netlify, linked from a "🚀 Full Portfolio →" button
in this README. That's also a much stronger project to show off than the
README itself — happy to scaffold that with you as its own build whenever
you're ready to start it.
