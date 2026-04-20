#!/usr/bin/env python3
import json, time, urllib.request, os
 
GBFS_STATION_INFO   = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pl/pl/station_information.json"
GBFS_STATION_STATUS = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pl/pl/station_status.json"
 
DATA_FILE     = "data.json"
MAX_SNAPSHOTS = 8760
 
def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VeturiloDashboard/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
 
def fetch():
    print("Pobieram station_information...")
    info_raw = get_json(GBFS_STATION_INFO)
 
    stations_info = info_raw["data"]["stations"]
    print(f"Łączna liczba stacji w feedzie: {len(stations_info)}")
 
    # pokaż 3 przykładowe żeby zobaczyć współrzędne
    for s in stations_info[:3]:
        print(f"  PRZYKŁAD: {json.dumps(s, ensure_ascii=False)[:300]}")
 
    print("Pobieram station_status...")
    status_raw = get_json(GBFS_STATION_STATUS)
    print(f"Łączna liczba statusów: {len(status_raw['data']['stations'])}")
    print(f"  STATUS przykład: {json.dumps(status_raw['data']['stations'][0], ensure_ascii=False)[:200]}")
 
def main():
    fetch()
 
main()
