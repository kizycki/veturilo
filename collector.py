#!/usr/bin/env python3
import json, time, urllib.request, os

API_URL       = "https://maps.nextbike.net/maps/nextbike-official.json?city=210,372,475"
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760

def fetch():
    req = urllib.request.Request(API_URL,
          headers={"User-Agent": "VeturiloDashboard/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = json.loads(r.read().decode())

    countries = raw.get("countries", [])
    print(f"DEBUG: liczba countries = {len(countries)}")

    if countries:
        c0 = countries[0]
        print(f"DEBUG country[0] keys: {list(c0.keys())}")
        # wypisz wszystkie klucze i typy wartości
        for k, v in c0.items():
            if isinstance(v, list):
                print(f"  kraj['{k}'] = lista {len(v)} elementów")
                if v and isinstance(v[0], dict):
                    print(f"    pierwszy element keys: {list(v[0].keys())}")
                    # zejdź jeszcze poziom niżej
                    for k2, v2 in v[0].items():
                        if isinstance(v2, list):
                            print(f"      ['{k2}'] = lista {len(v2)} elementów")
                            if v2 and isinstance(v2[0], dict):
                                print(f"        przykład: {json.dumps(v2[0], ensure_ascii=False)[:400]}")
            else:
                print(f"  kraj['{k}'] = {repr(v)[:80]}")

    return []  # na razie tylko debug, nie zapisujemy

def main():
    fetch()
    print("DEBUG zakończony – sprawdź logi powyżej")

main()
