#!/usr/bin/env python3
"""
Fetch Rishabh's pull-request counts from the public, unauthenticated
GitHub search API and write them to data/prs.json for render_readme_cards.py.

Counts are EXTERNAL repos only (his own r1shabhsharma05/* repos excluded),
the same definition the resume and portfolio use: "22 pull requests merged
and 8 open". The search API returns at most 100 items per call; merged total
is ~34 and open ~9, so one page each covers it. On any failure (network,
rate limit, bad response) this prints a warning and exits 0 WITHOUT touching
data/prs.json, so the renderer keeps using the last good numbers instead of
failing the daily run.

Run by .github/workflows/update-profile-art.yml before render_readme_cards.py.
"""
import datetime
import json
import os

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT_PATH = os.path.join(ROOT, "data", "prs.json")

USER = "r1shabhsharma05"
SEARCH_URL = "https://api.github.com/search/issues"
OWN_PREFIX = f"https://api.github.com/repos/{USER}/"


def count(query):
    """(external, total) PRs matching a search query."""
    r = requests.get(SEARCH_URL, params={"q": query, "per_page": 100}, timeout=20)
    r.raise_for_status()
    items = r.json()["items"]
    external = [it for it in items if not it["repository_url"].startswith(OWN_PREFIX)]
    return len(external), len(items)


def main():
    try:
        merged_ext, merged_total = count(f"type:pr author:{USER} is:merged")
        open_ext, open_total = count(f"type:pr author:{USER} is:open")
        out = {
            "merged_external": merged_ext,
            "open_external": open_ext,
            "merged_total": merged_total,
            "open_total": open_total,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    except Exception as e:  # keep the daily run green; renderer falls back
        print(f"prs fetch failed (keeping last good data): {e}")
        return
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH}: {out['merged_external']} merged / "
          f"{out['open_external']} open (external repos)")


if __name__ == "__main__":
    main()
