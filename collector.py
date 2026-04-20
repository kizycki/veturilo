#!/usr/bin/env python3
import json, time, urllib.request, os

DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760

# Kilka możliwych feedów Nextbike dla Warszawy
FEEDS = [
    "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wa/pl/station_information.json",
    "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_waw/pl/station_information.json",
    "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ve/pl/station_information.json",
    "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vl/pl/station_information.json",
]

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def try_feed(url):
    try:
        data = get_json(url)
        stations = data["data"]["stations"]
        if stations:
            s = stations[0]
            print(f"  OK: {url}")
            print(f"     {len(stations)} stacji, przykład: {s['name']} lat={s['lat']}")
        else:
            print(f"  PUSTY: {url}")
    except Exception as e:
        print(f"  BŁĄD: {url} -> {e}")

def main():
    print("Szukam właściwego feedu dla Warszawy...")
    for f in FEEDS:
        try_feed(f)

    # Spróbuj też pobrać listę wszystkich feedów
    print("\nSprawdzam główny katalog GBFS Nextbike...")
    try:
        data = get_json("https://gbfs.nextbike.net/maps/gbfs/v2/gbfs.json")
        print(f"  Klucze: {list(data.keys())}")
        print(f"  Dane: {json.dumps(data)[:500]}")
    except Exception as e:
        print(f"  BŁĄD: {e}")

main()
