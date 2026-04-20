#!/usr/bin/env python3
"""
Veturilo collector – Warszawa (uid=812) + Piaseczno (uid=461)
Uruchamiany przez GitHub Actions co godzinę.
"""
import json, time, urllib.request, os

CITY_IDS  = [812, 461]   # Warszawa, Piaseczno
API_URL   = "https://api.nextbike.net/maps/nextbike-live.json?city=" + ",".join(str(c) for c in CITY_IDS)
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def fetch():
    data = get_json(API_URL)

    seen, stations = set(), []
    for country in data.get("countries", []):
        for city in country.get("cities", []):
            city_name = city.get("name", "")
            for place in city.get("places", []):
                uid = place.get("uid")
                name = (place.get("name") or "").strip()
                if not name or uid in seen:
                    continue
                seen.add(uid)
                bikes = place.get("bikes", 0)
                stations.append({
                    "uid":   uid,
                    "name":  name,
                    "num":   str(place.get("number", place.get("station_number", ""))),
                    "bikes": int(bikes) if str(bikes).isdigit() else 0,
                    "city":  city_name,
                    "lat":   place.get("lat"),
                    "lng":   place.get("lng"),
                })

    return sorted(stations, key=lambda x: (x["city"], x["name"]))

def main():
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []

    stations = fetch()
    history.append({"ts": int(time.time() * 1000), "stations": stations})
    history = history[-MAX_SNAPSHOTS:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, separators=(",", ":"))

    total = sum(s["bikes"] for s in stations)
    waw   = sum(1 for s in stations if s["city"] == "Warszawa")
    pia   = sum(1 for s in stations if s["city"] != "Warszawa")
    print(f"OK – {len(stations)} stacji ({waw} Warszawa, {pia} Piaseczno), {total} rowerów łącznie.")

main()
