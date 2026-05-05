#!/usr/bin/env python3
import json, urllib.request, re

CITY_IDS = [812, 461]
API_URL  = "https://api.nextbike.net/maps/nextbike-live.json?city=" + ",".join(str(c) for c in CITY_IDS)

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def is_free_floating(name):
    return bool(re.match(r'^(BIKE\s*)?\d+$', name.strip(), re.IGNORECASE))

def main():
    data = get_json(API_URL)

    print("=== PIERWSZE 5 ROWERÓW FREE-FLOATING (pełne dane) ===")
    count = 0
    for country in data.get("countries", []):
        for city in country.get("cities", []):
            for place in city.get("places", []):
                name = (place.get("name") or "").strip()
                if is_free_floating(name):
                    print(json.dumps(place, ensure_ascii=False, indent=2))
                    count += 1
                    if count >= 5:
                        return

main()
