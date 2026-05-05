# Veturilo – monitor stacji rowerowych

Monitor dostępności rowerów Veturilo w Warszawie i Piasecznie. Dane zbierane co godzinę automatycznie przez GitHub Actions, prezentowane na dashboardzie i mapie dostępnych przez GitHub Pages.

---

## Pliki w repozytorium

| Plik | Opis |
|------|------|
| `collector.py` | Skrypt pobierający dane z API Nextbike |
| `dashboard.html` | Dashboard z wykresami historii dostępności |
| `map.html` | Mapa stacji z aktualnym stanem |
| `stations.json` | Metadane stacji (nazwa, nr, współrzędne) – generowany automatycznie |
| `data.json` | Historia pomiarów w formacie kompaktowym – generowany automatycznie |
| `bikes_YYYY_MM.json` | Numery rowerów per stacja, rotowany miesięcznie – do analizy przepływu |
| `.github/workflows/collect.yml` | Definicja workflow GitHub Actions |

---

## Architektura

```
cron-job.org (co godzinę)
    └─► GitHub Actions (collect.yml)
            └─► collector.py
                    ├─► stations.json   (metadane stacji, ~50 KB, stały)
                    ├─► data.json       (historia: ts + {uid:bikes} + ff_count, ~3 KB/pomiar)
                    └─► bikes_YYYY_MM.json  (numery rowerów, rotowany miesięcznie)

GitHub Pages
    ├─► dashboard.html  (wykresy historii)
    └─► map.html        (mapa z aktualnym stanem)
```

**Rozmiar danych po roku:** ~29 MB (`data.json`) + ~34 MB/miesiąc (`bikes_YYYY_MM.json`)

---

## Dashboard

Dostępny pod adresem: `https://TWOJA-NAZWA.github.io/veturilo/dashboard.html`

Funkcje:
- Statystyki bieżące (liczba stacji, rowerów, pustych stacji, rowerów poza stacjami)
- Wykres łącznej liczby rowerów na stacjach w czasie
- Wykres liczby rowerów poza stacjami (free-floating) w czasie
- Wykres historii wybranych stacji (kliknij stację w tabeli, max 6)
- Filtr zakresu czasu: 24h / 7 dni / 30 dni / Wszystko
- Tabela stacji z aktualnym stanem i zmianą względem poprzedniego pomiaru

## Mapa

Dostępna pod adresem: `https://TWOJA-NAZWA.github.io/veturilo/map.html`

Funkcje:
- Kolorowe kropki na każdej stacji (zielona ≥3 rowery, żółta 1–2, czerwona pusta)
- Rozmiar kropki proporcjonalny do liczby rowerów
- Popup po kliknięciu: nazwa stacji, numer, liczba rowerów
- Filtry: Wszystkie / Mało (≤2) / Puste
- Automatyczne odświeżanie co minutę

---

## Konfiguracja automatycznego zbierania danych

Dane zbierane są przez **GitHub Actions** wyzwalane przez **cron-job.org** co godzinę.

### GitHub Actions (`collect.yml`)
Workflow uruchamia `collector.py`, który pobiera dane i commituje pliki do repozytorium. Wymaga ustawienia **Read and write permissions** w Settings → Actions → General → Workflow permissions.

### cron-job.org
Zewnętrzny serwis wysyła co godzinę żądanie POST do GitHub API wyzwalające workflow:

- **URL:** `https://api.github.com/repos/TWOJA-NAZWA/veturilo/actions/workflows/collect.yml/dispatches`
- **Method:** POST
- **Headers:**
  - `Accept: application/vnd.github.v3+json`
  - `Authorization: Bearer TWÓJ_GITHUB_TOKEN`
- **Body:** `{"ref":"main"}`

GitHub Personal Access Token wymaga scope: `workflow`.

---

## Konfiguracja kolektora

W pliku `collector.py` można zmienić:

```python
CITY_IDS      = [812, 461]  # Warszawa, Piaseczno
MAX_SNAPSHOTS = 8760        # maks. historia (8760 = 365 dni × 24h)
```

Żeby dodać inne miasto, znajdź jego `uid` przez API:
```
https://api.nextbike.net/maps/nextbike-live.json?list_cities=1
```

---

## Wymagania

- Python 3.6+
- Brak dodatkowych bibliotek – używa tylko standardowej biblioteki Pythona
- Konto GitHub (darmowe)
- Konto cron-job.org (darmowe)
