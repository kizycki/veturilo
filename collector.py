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

    # ── DEBUG: pokaż strukturę odpowiedzi ──────────────────────────
    top_keys = list(raw.keys())
    print(f"DEBUG top-level keys: {top_keys}")

    for top_key in top_keys:
        val = raw[top_key]
        if isinstance(val, list) and val:
            print(f"DEBUG raw['{top_key}'] = list of {len(val)}, first item keys: {list(val[0].keys()) if isinstance(val[0], dict) else type(val[0])}")
            first = val[0]
            for k, v in first.items():
                if isinstance(v, list) and v:
                    print(f"  DEBUG first['{k}'] = list of {len(v)}, sample keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}")
                    inner = v[0]
                    for k2, v2 in inner.items():
                        if isinstance(v2, list) and v2:
                            print(f"    DEBUG [{k}][0]['{k2}'] = list of {len(v2)}, sample keys: {list(v2[0].keys()) if isinstance(v2[0], dict) else type(v2[0])}")
                            if v2:
                                print(f"    SAMPLE PLACE: {json.dumps(v2[0], ensure_ascii=False)[:400]}")
    # ── koniec DEBUG ───────────────────────────────────────────────

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
