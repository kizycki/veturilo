#!/usr/bin/env python3
"""
Veturilo collector – Warszawa (uid=812) + Piaseczno (uid=461)
Stacje i rowery free-floating trzymane osobno.
"""
import json, time, urllib.request, os, re

CITY_IDS  = [812, 461]
API_URL   = "https://api.nextbike.net/maps/nextbike-live.json?city=" + ",".join(str(c) for c in CITY_IDS)
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def is_free_floating(name):
    """Rower poza stacją ma nazwę BIKE 123456 lub samą liczbę."""
    return bool(re.match(r'^(BIKE\s*)?\d+$', name.strip(), re.IGNORECASE))

def fetch():
    data = get_json(API_URL)

    seen, stations, free_floating = set(), [], []

    for country in data.get("countries", []):
        for city in country.get("cities", []):
            city_name = city.get("name", "")
            for place in city.get("places", []):
                uid = place.get("uid")
                name = (place.get("name") or "").strip()
                if not name or uid in seen:
                    continue
                seen.add(uid)

                bike_numbers = []
                for bike in place.get("bike_list", []):
                    num = bike.get("number") or bike.get("bike_number")
                    if num:
                        bike_numbers.append(str(num))

                bikes = place.get("bikes", 0)
                bikes = int(bikes) if str(bikes).isdigit() else 0

                if is_free_floating(name):
                    # rower poza stacją – zapisz tylko numer
                    free_floating.extend(bike_numbers if bike_numbers else [name])
                else:
                    stations.append({
                        "uid":       uid,
                        "name":      name,
                        "num":       str(place.get("number", place.get("station_number", ""))),
                        "bikes":     bikes,
                        "bike_list": bike_numbers,
                        "city":      city_name,
                        "lat":       place.get("lat"),
                        "lng":       place.get("lng"),
                    })

    stations.sort(key=lambda x: (x["city"], x["name"]))
    return stations, free_floating

def main():
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []

    stations, free_floating = fetch()
    history.append({
        "ts":           int(time.time() * 1000),
        "stations":     stations,
        "free_floating": free_floating,   # lista numerów rowerów poza stacjami
    })
    history = history[-MAX_SNAPSHOTS:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, separators=(",", ":"))

    total = sum(s["bikes"] for s in stations)
    waw   = sum(1 for s in stations if s["city"] == "Warszawa")
    pia   = sum(1 for s in stations if s["city"] != "Warszawa")
    print(f"OK – {len(stations)} stacji ({waw} Warszawa, {pia} Piaseczno), {total} rowerów na stacjach, {len(free_floating)} poza stacjami.")

main()
