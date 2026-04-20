# Veturilo – monitor stacji rowerowych

## Co jest w tym folderze

| Plik | Co robi |
|------|---------|
| `collector.py` | Działa 24/7, co godzinę pobiera dane i zapisuje do `data.json` |
| `dashboard.html` | Strona do przeglądania w przeglądarce. Czyta `data.json` |
| `data.json` | Tworzy się automatycznie po pierwszym uruchomieniu collectora |

---

## Szybki start (na swoim komputerze)

### 1. Uruchom kolektor

Potrzebujesz **Pythona 3** (sprawdź: `python --version` lub `python3 --version`)

```bash
python collector.py
```

lub

```bash
python3 collector.py
```

Kolektor:
- od razu pobierze pierwsze dane
- następnie będzie pobierał co godzinę
- wypisuje logi w terminalu

**Zostaw terminal otwarty** (albo uruchom w tle – patrz niżej).

### 2. Otwórz dashboard

Otwórz `dashboard.html` w przeglądarce. Gotowe.

---

## Uruchomienie 24/7

### Windows – uruchomienie w tle (Task Scheduler)

1. Wyszukaj „Harmonogram zadań" w menu Start
2. Utwórz zadanie: `python C:\sciezka\do\collector.py`
3. Wyzwalacz: „Przy uruchomieniu komputera"

### macOS / Linux – uruchomienie w tle

```bash
nohup python3 collector.py > collector.log 2>&1 &
```

Żeby sprawdzić czy działa:
```bash
tail -f collector.log
```

### Raspberry Pi / serwer Linux – systemd (polecane)

Utwórz plik `/etc/systemd/system/veturilo.service`:

```ini
[Unit]
Description=Veturilo collector
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/veturilo/collector.py
WorkingDirectory=/home/pi/veturilo
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Następnie:
```bash
sudo systemctl enable veturilo
sudo systemctl start veturilo
sudo systemctl status veturilo   # sprawdź czy działa
```

---

## Udostępnienie innym osobom

### Opcja A: wyślij plik (najprostsze)

Po zebraniu danych (np. po kilku godzinach) skopiuj `data.json` i `dashboard.html` do jednego folderu i prześlij komuś np. przez e-mail lub Dropbox. Osoba otwiera `dashboard.html` bezpośrednio – dane są wbudowane.

### Opcja B: prosty serwer HTTP (dostęp przez sieć lokalną)

```bash
cd /sciezka/do/folderu
python3 -m http.server 8080
```

Inni w tej samej sieci WiFi wchodzą pod:
```
http://TWÓJ-IP:8080/dashboard.html
```

Twoje IP znajdziesz przez `ipconfig` (Windows) lub `ip addr` (Linux/Mac).

### Opcja C: GitHub Pages (bezpłatnie, dostęp z internetu)

1. Utwórz repozytorium na GitHub
2. Wrzuć `dashboard.html` i `data.json`
3. Włącz GitHub Pages w ustawieniach repo
4. Ustaw `collector.py` żeby commitował `data.json` co godzinę (przez `git push`)

---

## Konfiguracja

W pliku `collector.py` możesz zmienić:

```python
INTERVAL_SEC  = 3600   # co ile sekund pobierać (3600 = 1 godzina)
MAX_SNAPSHOTS = 8760   # maks. historia (8760 = 365 dni × 24h)
```

---

## Wymagania

- Python 3.6+
- Brak dodatkowych bibliotek – używa tylko standardowej biblioteki
