"""
Charuka OS — Intelligence Engine
Pulls live data from the GitHub API and:
  1. Regenerates assets/digital_dna.svg  (skill bars, weighted by real repo/language data)
  2. Injects live numbers into README.md between the <!--LIVE_PULSE_START--> / END markers

Run by .github/workflows/update-readme.yml on a daily schedule + manual dispatch.
Requires: GITHUB_TOKEN (auto-provided by Actions) and GITHUB_REPOSITORY_OWNER env vars.
"""

import os
import re
import sys
import json
import datetime
import urllib.request

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "CharukaNWickramarachchi")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"

# Map GitHub's per-language byte counts onto the "Digital DNA" categories.
# Extend this as you use more languages/tools.
DNA_CATEGORIES = {
    "Python":     ["Python"],
    "Data/SQL":   ["SQL", "PLpgSQL", "Jupyter Notebook"],
    "Web/App":    ["HTML", "CSS", "JavaScript", "TypeScript"],
    "R/Stats":    ["R"],
    "Other":      [],  # catch-all, filled in below
}


def gh_get(path):
    req = urllib.request.Request(f"{API}{path}", headers={
        "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
        "Accept": "application/vnd.github+json",
        "User-Agent": USERNAME,
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_repos():
    repos, page = [], 1
    while True:
        batch = gh_get(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        page += 1
        if page > 10:
            break
    return repos


def fetch_language_totals(repos):
    totals = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            langs = gh_get(f"/repos/{USERNAME}/{r['name']}/languages")
        except Exception:
            continue
        for lang, byte_count in langs.items():
            totals[lang] = totals.get(lang, 0) + byte_count
    return totals


def build_dna_scores(lang_totals):
    total_bytes = sum(lang_totals.values()) or 1
    scores = {}
    used_langs = set()
    for category, langs in DNA_CATEGORIES.items():
        if category == "Other":
            continue
        cat_bytes = sum(lang_totals.get(l, 0) for l in langs)
        used_langs.update(langs)
        scores[category] = round(100 * cat_bytes / total_bytes)
    other_bytes = sum(b for l, b in lang_totals.items() if l not in used_langs)
    scores["Other"] = round(100 * other_bytes / total_bytes)
    # Normalize to a 0-100 "confidence" scale, floor at 5 so bars stay visible
    for k in scores:
        scores[k] = max(scores[k], 5) if scores[k] > 0 else 0
    return scores


def render_dna_svg(scores):
    bar_w = 420
    row_h = 34
    pad_top = 30
    width = 560
    height = pad_top + row_h * len(scores) + 20

    rows = []
    y = pad_top
    for i, (label, pct) in enumerate(scores.items()):
        filled = int(bar_w * min(pct, 100) / 100)
        rows.append(f'''
    <text x="10" y="{y+16}" fill="#c9d1d9" font-family="'Fira Code', monospace" font-size="13">{label}</text>
    <rect x="150" y="{y}" width="{bar_w}" height="16" rx="8" fill="#1b2430"/>
    <rect x="150" y="{y}" width="{filled}" height="16" rx="8" fill="url(#grad)">
      <animate attributeName="width" from="0" to="{filled}" dur="1.2s" fill="freeze"/>
    </rect>
    <text x="{150+bar_w+10}" y="{y+16}" fill="#00c6ff" font-family="'Fira Code', monospace" font-size="12">{pct}%</text>''')
        y += row_h

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00c6ff"/>
      <stop offset="100%" stop-color="#0f2027"/>
    </linearGradient>
  </defs>
  <text x="10" y="18" fill="#8b949e" font-family="'Fira Code', monospace" font-size="12">CHARUKA DIGITAL DNA — live, generated from repo language data</text>
  {''.join(rows)}
</svg>'''
    return svg


def update_readme_pulse(repos):
    active = [r for r in repos if not r.get("fork")]
    languages = {}
    for r in active:
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    top_lang = max(languages, key=languages.get) if languages else "N/A"

    last_pushed = max((r["pushed_at"] for r in active if r.get("pushed_at")), default=None)
    if last_pushed:
        dt = datetime.datetime.strptime(last_pushed, "%Y-%m-%dT%H:%M:%SZ")
        delta = datetime.datetime.utcnow() - dt
        hours = int(delta.total_seconds() // 3600)
        last_activity = f"{hours}h ago" if hours < 48 else f"{hours//24}d ago"
    else:
        last_activity = "N/A"

    block = f"""<!--LIVE_PULSE_START-->
| | |
|---|---|
| 📦 **Public repositories** | {len(active)} |
| 🕓 **Last push** | {last_activity} |
| 🔤 **Most used language** | {top_lang} |
| 🔄 **Last synced** | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} |
<!--LIVE_PULSE_END-->"""

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!--LIVE_PULSE_START-->.*?<!--LIVE_PULSE_END-->",
        block,
        content,
        flags=re.DOTALL,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    try:
        repos = fetch_repos()
    except Exception as e:
        print(f"Failed to fetch repos: {e}", file=sys.stderr)
        sys.exit(0)  # don't fail the whole workflow over a transient API error

    try:
        lang_totals = fetch_language_totals(repos)
        scores = build_dna_scores(lang_totals)
        os.makedirs("assets", exist_ok=True)
        with open("assets/digital_dna.svg", "w", encoding="utf-8") as f:
            f.write(render_dna_svg(scores))
    except Exception as e:
        print(f"Failed to build Digital DNA svg: {e}", file=sys.stderr)

    try:
        update_readme_pulse(repos)
    except Exception as e:
        print(f"Failed to update README pulse: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
