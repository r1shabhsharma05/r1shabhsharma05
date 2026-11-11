#!/usr/bin/env python3
"""
Fetch Rishabh's LeetCode solved counts from the public, unauthenticated
GraphQL endpoint and write them to data/leetcode.json for render_readme_cards.py.

No token needed: matchedUser + submitStatsGlobal are public. On any failure
(network, bad response, unknown username) this prints a warning and exits 0
WITHOUT touching data/leetcode.json, so the renderer keeps using the last good
numbers (or its hand-set fallback constants) instead of failing the daily run.

Run by .github/workflows/update-profile-art.yml before render_readme_cards.py.
"""
import datetime
import json
import os

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT_PATH = os.path.join(ROOT, "data", "leetcode.json")

USERNAME = "rishabh_sharma__"
URL = "https://leetcode.com/graphql"
QUERY = """
query { matchedUser(username: "%s") {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
} }
""" % USERNAME


def main():
    try:
        r = requests.post(URL, json={"query": QUERY}, timeout=20)
        r.raise_for_status()
        nums = r.json()["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        by_diff = {n["difficulty"]: n["count"] for n in nums}
        out = {
            "username": USERNAME,
            "solved": by_diff["All"],
            "easy": by_diff["Easy"],
            "medium": by_diff["Medium"],
            "hard": by_diff["Hard"],
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    except Exception as e:  # keep the daily run green; renderer falls back
        print(f"leetcode fetch failed (keeping last good data): {e}")
        return
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH}: {out['solved']} solved "
          f"({out['easy']} Easy / {out['medium']} Medium / {out['hard']} Hard)")


if __name__ == "__main__":
    main()
