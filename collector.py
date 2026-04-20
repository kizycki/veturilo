#!/usr/bin/env python3
import json, urllib.request

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    # Pobierz listę wszystkich sieci Nextbike na świecie
    print("Pobieram listę wszystkich sieci Nextbike...")
    data = get_json("https://api.nextbike.net/maps/nextbike-live.json?list_cities=1")
    
    # Znajdź wszystko co ma "warsaw" lub "veturilo" lub "pl" w nazwie/domenie
    for country in data.get("countries", []):
        for city in country.get("cities", []):
            name = city.get("name", "").lower()
            domain = city.get("domain", "").lower()
            website = city.get("website", "").lower()
            uid = city.get("uid", "")
            if any(k in name+domain+website for k in ["warsaw","veturilo","warsow","varso"]):
                print(f"ZNALEZIONO: uid={uid} name={city.get('name')} domain={domain} website={website}")
                print(f"  pełne dane: {json.dumps(city, ensure_ascii=False)[:400]}")

    print("\nWszystkie polskie miasta:")
    for country in data.get("countries", []):
        if "poland" in country.get("name","").lower() or country.get("country","") == "PL":
            print(f"Kraj: {country.get('name')} ({country.get('country')})")
            for city in country.get("cities", []):
                print(f"  uid={city.get('uid')} name={city.get('name')} domain={city.get('domain')} lat={city.get('lat')}")

main()
