#!/usr/bin/env python3
"""
Veturilo collector – uruchamiany przez GitHub Actions co godzinę.
Dopisuje nowy pomiar do data.json (maks. 8760 wpisów = 365 dni).
"""
import json, time, urllib.request, os

API_URL       = "https://maps.nextbike.net/maps/nextbike-official.json?city=210,372,475"
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760

def fetch():
    req = urllib.request.Request(API_URL,
          headers={"User-Agent": "VeturiloDashboard/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = json.loads(r.read().decode())

    seen, stations = set(), []
    for country in raw.get("countries", []):
        for city in country.get("cities", []):
            for p in city.get("places", []):
                uid = p.get("uid")
                if not p.get("name") or uid in seen:
                    continue
                seen.add(uid)
                bikes = p.get("bikes", 0)
                stations.append({
                    "uid":   uid,
                    "name":  p["name"].strip(),
                    "num":   str(p.get("number", p.get("station_number", ""))),
                    "bikes": int(bikes) if str(bikes).isdigit() else 0,
                    "lat":   p.get("lat"),
                    "lng":   p.get("lng"),
                })
    return sorted(stations, key=lambda x: x["name"])

def main():
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            history = json.load(f)

    stations = fetch()
    history.append({"ts": int(time.time() * 1000), "stations": stations})
    history = history[-MAX_SNAPSHOTS:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, separators=(",", ":"))

    total = sum(s["bikes"] for s in stations)
    print(f"OK – {len(stations)} stacji, {total} rowerów.")

main()
