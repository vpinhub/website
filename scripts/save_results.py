#!/usr/bin/env python3
"""
Fetch competition results from the iScored API and save to the JSON archive.

Usage:
    python scripts/save_results.py swl
    python scripts/save_results.py ttd

Run from the repo root. Writes to competition/json/ and updates list.json.
"""

import json
import random
import re
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

EASTERN = ZoneInfo("America/New_York")

COMPETITIONS = {
    "swl": {
        "prefix": "Special_When_Lit",
        "room_id": "1011",
        "cutoff_weekday": 6,   # Sunday  (Python weekday: Mon=0 … Sun=6)
        "cutoff_hour": 14,
        "override_key": "swl",
    },
    "ttd": {
        "prefix": "Thursday_Throwdown",
        "room_id": "700",
        "cutoff_weekday": 3,   # Thursday
        "cutoff_hour": 14,
        "override_key": "ttd",
    },
}

ISCORED_API = "https://virtualpinballchat.com/vpc/api/v1/iscored?roomId={room_id}"
VPS_API     = "https://raw.githubusercontent.com/VirtualPinballSpreadsheet/vps-db/main/db/vpsdb.json"
OVERRIDE_FILE = "competition/override.json"
LIST_FILE     = "competition/json/list.json"
JSON_DIR      = "competition/json"


# ---------------------------------------------------------------------------
# Period calculation — mirrors calculateSWLPeriod / calculateTTDPeriod in JS
# ---------------------------------------------------------------------------

def get_period(cutoff_weekday: int, cutoff_hour: int) -> tuple[str, str]:
    now = datetime.now(tz=EASTERN)
    days_ahead = (cutoff_weekday - now.weekday()) % 7
    # If today is cutoff day but the cutoff has already passed, jump a week
    if days_ahead == 0 and now.hour >= cutoff_hour:
        days_ahead = 7
    end = (now + timedelta(days=days_ahead)).replace(
        hour=cutoff_hour, minute=0, second=0, microsecond=0
    )
    start = end - timedelta(days=7)
    fmt = "%-m/%-d/%Y"
    return start.strftime(fmt), end.strftime(fmt)


# ---------------------------------------------------------------------------
# Score processing — mirrors processTournament in JS
# ---------------------------------------------------------------------------

def process_scores(scores: list, override: dict | None) -> tuple[list, dict]:
    # Drop the sentinel "init" / 0 entries
    scores = [
        s for s in scores
        if not (s.get("name", "").lower() == "init" and int(s.get("score", 0)) == 0)
    ]
    if not scores:
        return [], {}

    player_stats: dict[str, dict] = {}
    pioneer = {"name": "N/A", "date": float("inf")}

    for s in scores:
        val = int(s.get("score", 0))
        raw_date = s.get("date_added") or s.get("date") or s.get("timestamp")
        try:
            ts = datetime.fromisoformat(
                raw_date.replace("Z", "+00:00")
            ).timestamp() if raw_date else float("inf")
        except Exception:
            ts = float("inf")

        if ts < pioneer["date"]:
            pioneer = {"name": s["name"], "date": ts}

        name = s["name"]
        if name not in player_stats:
            player_stats[name] = {
                "name": name,
                "scores": [],
                "raw_entries": [],
                "high": 0,
                "low": float("inf"),
                "total": 0,
            }
        p = player_stats[name]
        p["scores"].append(val)
        p["total"] += val
        p["raw_entries"].append({"val": val, "time": ts})
        if val > p["high"]:
            p["high"] = val
        if val < p["low"]:
            p["low"] = val

    player_list = []
    for p in player_stats.values():
        p["avg"] = p["total"] / len(p["scores"])
        p["raw_entries"].sort(key=lambda e: e["time"])
        p["comeback_growth"] = (
            p["raw_entries"][-1]["val"] - p["raw_entries"][0]["val"]
            if len(p["raw_entries"]) > 1 else 0
        )
        p["improvement_gap"] = p["high"] - p["low"]
        player_list.append(p)

    results = sorted(player_list, key=lambda p: p["high"], reverse=True)

    shooter  = max(player_list, key=lambda p: p["avg"],              default=None)
    grinder  = max(player_list, key=lambda p: len(p["scores"]),      default=None)
    burns    = random.choice(player_list) if player_list else None

    improved_list  = sorted(player_list, key=lambda p: p["improvement_gap"],  reverse=True)
    comeback_list  = sorted(player_list, key=lambda p: p["comeback_growth"],   reverse=True)
    improved = improved_list[0]  if improved_list  else None
    comeback = comeback_list[0]  if comeback_list  else None

    if improved and comeback and improved["name"] == comeback["name"]:
        comeback = comeback_list[1] if len(comeback_list) > 1 else None

    wooden = None
    if len(results) > 2:
        candidates = [p for p in results[1:-1] if p["improvement_gap"] > 0]
        if candidates:
            wooden = candidates[-1]

    billionaire = next((p for p in results if p["high"] >= 1_000_000_000), None)
    nice_award  = next((p for p in results if str(p["high"]).startswith("69")), None)

    pir = None
    closest = 5.0
    for i in range(1, len(results)):
        ahead = results[i - 1]
        curr  = results[i]
        if ahead["high"] > 0:
            margin = ((ahead["high"] - curr["high"]) / ahead["high"]) * 100
            if margin <= 5.0 and margin < closest:
                closest = margin
                pir = {"name": curr["name"], "detail": f"Closest to {ahead['name']}"}

    awards = {
        "winner":               results[0]["name"]            if results    else None,
        "fast_draw":            pioneer["name"],
        "fast_draw_detail":     "First Entry",
        "sharpshooter":         shooter["name"]               if shooter    else None,
        "sharpshooter_detail":  "Top Average",
        "most_improved":        improved["name"]              if improved   else None,
        "most_improved_detail": f"Gap: +{improved['improvement_gap']:,}" if improved else None,
        "comeback_kid":         comeback["name"]              if comeback   else None,
        "comeback_kid_detail":  f"Gain: +{comeback['comeback_growth']:,}" if comeback else None,
        "most_played":          grinder["name"]               if grinder    else None,
        "most_played_detail":   f"{len(grinder['scores'])} Games" if grinder else None,
        "burns_award":          burns["name"]                 if burns      else None,
        "burns_award_detail":   "Excellent!",
        "wooden_spoon":         wooden["name"]                if wooden     else None,
        "wooden_spoon_detail":  "I'm a lumberjack!",
        "price_is_right":       pir["name"]                   if pir        else None,
        "price_is_right_detail":pir["detail"]                 if pir        else None,
        "billionaire":          billionaire["name"]            if billionaire else None,
        "billionaire_detail":   "Score > 1,000,000,000",
        "nice_award":           nice_award["name"]             if nice_award  else None,
        "nice_award_detail":    "Nice!",
    }

    export_results = [
        {
            "name":             p["name"],
            "high":             p["high"],
            "low":              p["low"] if p["low"] != float("inf") else 0,
            "avg":              round(p["avg"], 2),
            "total":            p["total"],
            "scores":           p["scores"],
            "improvement_gap":  p["improvement_gap"],
            "comeback_growth":  p["comeback_growth"],
        }
        for p in results
    ]

    return export_results, awards


# ---------------------------------------------------------------------------
# Table name resolution — mirrors renderTable tag-match logic in JS
# ---------------------------------------------------------------------------

def resolve_table_name(tournament_game: dict, vps_db: list, override: dict | None) -> str:
    if override and override.get("tableName"):
        return override["tableName"]

    game_str  = json.dumps(tournament_game)
    tag_match = re.search(r'game=([a-zA-Z0-9\-_]+)[^#]*#([a-zA-Z0-9\-_]+)', game_str)
    if tag_match:
        game_id = tag_match.group(1)
        table   = next((t for t in vps_db if t.get("id") == game_id), None)
        if table:
            return table["name"]

    return tournament_game.get("longName") or "Unknown_Table"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMPETITIONS:
        print("Usage: python scripts/save_results.py swl|ttd")
        sys.exit(1)

    comp = COMPETITIONS[sys.argv[1]]
    print(f"▶ Saving results for {comp['prefix']}")

    # Fetch iScored data
    api_url    = ISCORED_API.format(room_id=comp["room_id"])
    score_resp = requests.get(api_url, timeout=30)
    score_resp.raise_for_status()
    score_data = score_resp.json()

    tournament_game = next(
        (g for g in score_data if "game=" in json.dumps(g)), score_data[0]
    )

    # Load override.json
    override = None
    try:
        with open(OVERRIDE_FILE) as f:
            override = json.load(f).get(comp["override_key"])
    except Exception as e:
        print(f"  override.json unavailable: {e}")

    # Fetch VPS DB
    vps_db = []
    try:
        vps_resp = requests.get(VPS_API, timeout=60)
        vps_db   = vps_resp.json()
        print(f"  VPS DB: {len(vps_db)} tables")
    except Exception as e:
        print(f"  VPS DB unavailable: {e}")

    table_name = resolve_table_name(tournament_game, vps_db, override)
    print(f"  Table: {table_name}")

    results, awards = process_scores(tournament_game.get("scores", []), override)
    if not results:
        print("  No scores found — aborting.")
        sys.exit(1)
    print(f"  Players: {len(results)}")

    start_str, end_str = get_period(comp["cutoff_weekday"], comp["cutoff_hour"])

    # Build filename to match the JS download name convention
    today          = datetime.now(tz=EASTERN).strftime("%Y-%m-%d")
    safe_name      = re.sub(r'[^a-zA-Z0-9]', '_', table_name)
    safe_name      = re.sub(r'_+', '_', safe_name).strip('_')
    filename       = f"{comp['prefix']}_{today}_{safe_name}.json"
    output_path    = f"{JSON_DIR}/{filename}"

    export_obj = {
        "competition":   comp["prefix"],
        "date_exported": datetime.now(tz=EASTERN).isoformat(),
        "period":        f"{start_str} - {end_str}",
        "table":         table_name,
        "awards":        awards,
        "results":       results,
    }

    with open(output_path, "w") as f:
        json.dump(export_obj, f, indent=4)
    print(f"  Written: {output_path}")

    # Update list.json (append if not already present)
    with open(LIST_FILE) as f:
        file_list = json.load(f)

    entry = {"name": filename, "path": f"json/{filename}"}
    if not any(e["name"] == filename for e in file_list):
        file_list.append(entry)
        with open(LIST_FILE, "w") as f:
            json.dump(file_list, f, indent=4)
        print(f"  list.json updated")
    else:
        print(f"  {filename} already in list.json — skipping update")

    print("✓ Done")


if __name__ == "__main__":
    main()
