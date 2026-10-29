"""Fetch Singapore's latest PSI readings from data.gov.sg (NEA) and save them
for the website in docs/data/. GitHub Actions runs this every hour."""
import json
import urllib.request
from pathlib import Path

URL = "https://api-open.data.gov.sg/v2/real-time/api/psi"
REGIONS = ["north", "south", "east", "west", "central"]
DATA_DIR = Path("docs/data")
HISTORY_LIMIT = 7 * 24  # keep about one week of hourly readings


def pick(readings, *names):
    for name in names:
        if name in readings:
            return readings[name]
    return {}


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "sg-haze-dashboard"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.load(resp)

    data = raw.get("data", raw)
    items = data.get("items") or []
    if not items:
        raise SystemExit("No PSI readings returned: " + json.dumps(raw)[:300])
    item = items[0]
    readings = item.get("readings", {})

    psi = pick(readings, "psi_twenty_four_hourly", "psiTwentyFourHourly")
    pm25 = pick(readings, "pm25_twenty_four_hourly", "pm25TwentyFourHourly")
    time = item.get("updatedTimestamp") or item.get("update_timestamp") or item.get("timestamp")

    latest = {
        "updated": time,
        "psi": {r: psi.get(r) for r in REGIONS},
        "pm25": {r: pm25.get(r) for r in REGIONS},
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "latest.json").write_text(json.dumps(latest, indent=2))

    history_file = DATA_DIR / "history.json"
    history = json.loads(history_file.read_text()) if history_file.exists() else []
    values = [v for v in latest["psi"].values() if isinstance(v, (int, float))]
    if values and not any(h["time"] == time for h in history):
        history.append({"time": time, "psi": max(values)})
    history_file.write_text(json.dumps(history[-HISTORY_LIMIT:], indent=2))

    print("Saved PSI for", time, latest["psi"])


if __name__ == "__main__":
    main()
