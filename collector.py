#!/usr/bin/env python3
"""
Veturilo collector – Warszawa (uid=812) + Piaseczno (uid=461)
Struktura plików:
  stations.json        – metadane stacji (nazwa, num, city, lat, lng) – aktualizowane gdy zmiana
  data.json            – historia pomiarów: ts + {uid: bikes} + ff_count
  bikes_YYYY_MM.json   – numery rowerów per stacja, rotowany miesięcznie
"""
import json, time, urllib.request, os, re
from datetime import datetime

CITY_IDS      = [812, 461]
API_URL       = "https://api.nextbike.net/maps/nextbike-live.json?city=" + ",".join(str(c) for c in CITY_IDS)
DATA_FILE     = "data.json"
STATIONS_FILE = "stations.json"
MAX_SNAPSHOTS = 8760

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def is_free_floating(name):
    return bool(re.match(r'^(BIKE\s*)?\d+$', name.strip(), re.IGNORECASE))

def fetch():
    data = get_json(API_URL)
    seen, stations, free_floating = set(), [], []

    for country in data.get("countries", []):
        for city in country.get("cities", []):
            city_name = city.get("name", "")
            for place in city.get("places", []):
                uid  = place.get("uid")
                name = (place.get("name") or "").strip()
                if not name or uid in seen:
                    continue
                seen.add(uid)

                bike_numbers = [str(b.get("number") or b.get("bike_number",""))
                                for b in place.get("bike_list", [])
                                if b.get("number") or b.get("bike_number")]

                bikes = place.get("bikes", 0)
                bikes = int(bikes) if str(bikes).isdigit() else 0

                if is_free_floating(name):
                    ff_entry = {
                        "num": bike_numbers[0] if bike_numbers else name,
                        "lat": place.get("lat"),
                        "lng": place.get("lng"),
                    }
                    free_floating.append(ff_entry)
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

def update_stations_meta(stations):
    """Zapisz/zaktualizuj stations.json gdy pojawi się nowa stacja lub zmiana nazwy."""
    existing = {}
    if os.path.exists(STATIONS_FILE):
        with open(STATIONS_FILE, encoding="utf-8") as f:
            for s in json.load(f):
                existing[s["uid"]] = s

    changed = False
    for s in stations:
        uid = s["uid"]
        meta = {"uid": uid, "name": s["name"], "num": s["num"], "city": s["city"], "lat": s["lat"], "lng": s["lng"]}
        if uid not in existing or existing[uid] != meta:
            existing[uid] = meta
            changed = True

    if changed:
        with open(STATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(existing.values()), f, ensure_ascii=False, separators=(",", ":"))
        print(f"stations.json zaktualizowany ({len(existing)} stacji).")

def save_bikes_detail(ts, stations, free_floating):
    """Zapisz numery rowerów do miesięcznego pliku bikes_YYYY_MM.json."""
    month_file = datetime.fromtimestamp(ts / 1000).strftime("bikes_%Y_%m.json")
    history = []
    if os.path.exists(month_file):
        with open(month_file, encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []

    snapshot = {
        "ts": ts,
        "s":  {str(s["uid"]): s["bike_list"] for s in stations if s["bike_list"]},
        "ff": [f["num"] for f in free_floating],
    }
    history.append(snapshot)

    with open(month_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, separators=(",", ":"))

def main():
    # wczytaj historię
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []

    stations, free_floating = fetch()

    ts = int(time.time() * 1000)

    # aktualizuj metadane stacji
    update_stations_meta(stations)

    # zapisz szczegółowe dane rowerów
    save_bikes_detail(ts, stations, free_floating)

    # lekki snapshot do dashboardu: tylko ts + {uid: bikes} + ff_count
    snapshot = {
        "ts": ts,
        "s":  {str(s["uid"]): s["bikes"] for s in stations},
        "ff": len(free_floating),
        "ff_loc": [{"num": f["num"], "lat": f["lat"], "lng": f["lng"]} for f in free_floating if f["lat"]],
    }
    history.append(snapshot)
    history = history[-MAX_SNAPSHOTS:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, separators=(",", ":"))

    total = sum(s["bikes"] for s in stations)
    waw   = sum(1 for s in stations if s["city"] == "Warszawa")
    pia   = sum(1 for s in stations if s["city"] != "Warszawa")
    print(f"OK – {len(stations)} stacji ({waw} Warszawa, {pia} Piaseczno), {total} rowerów, {len(free_floating)} poza stacjami (z GPS: {sum(1 for f in free_floating if f['lat'])}).")

main()
