#!/usr/bin/env python3
"""
Veturilo collector – używa GBFS (otwarty standard, bez blokad IP).
Łączy station_information + station_status żeby uzyskać nazwy i liczbę rowerów.
"""
import json, time, urllib.request, os
 
# GBFS endpointy Nextbike dla Polski
GBFS_STATION_INFO   = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pl/pl/station_information.json"
GBFS_STATION_STATUS = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pl/pl/station_status.json"
 
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760
 
# Współrzędne Warszawy – filtrujemy tylko stacje w promieniu ~30km
WAW_LAT, WAW_LNG, WAW_RADIUS = 52.23, 21.01, 0.35
 
def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
 
def fetch():
    print("Pobieram station_information...")
    info_raw  = get_json(GBFS_STATION_INFO)
    print("Pobieram station_status...")
    status_raw = get_json(GBFS_STATION_STATUS)
 
    # zbuduj mapę id -> info
    info_map = {}
    for s in info_raw["data"]["stations"]:
        lat = float(s.get("lat", 0))
        lng = float(s.get("lon", 0))
        # filtruj tylko Warszawę
        if abs(lat - WAW_LAT) < WAW_RADIUS and abs(lng - WAW_LNG) < WAW_RADIUS:
            info_map[s["station_id"]] = {
                "name": s.get("name", "").strip(),
                "num":  str(s.get("short_name", s["station_id"])),
                "lat":  lat,
                "lng":  lng,
            }
 
    print(f"Stacji w Warszawie (info): {len(info_map)}")
 
    # połącz ze statusem
    stations = []
    for s in status_raw["data"]["stations"]:
        sid = s["station_id"]
        if sid not in info_map:
            continue
        bikes = int(s.get("num_bikes_available", 0))
        stations.append({
            "uid":   sid,
            "name":  info_map[sid]["name"],
            "num":   info_map[sid]["num"],
            "bikes": bikes,
            "lat":   info_map[sid]["lat"],
            "lng":   info_map[sid]["lng"],
        })
 
    return sorted(stations, key=lambda x: x["name"])
 
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
    print(f"OK – {len(stations)} stacji, {total} rowerów łącznie.")
 
main()
