"""
tiedotteet_fetcher.py - V30 - manuaalinen Tiedotteet-kortti
- Luo data/tiedotteet.json jos ei ole
- Tarkistaa formaatin, ei ylikirjoita jos muokattu käsin
- Voit muokata tiedostoa suoraan GitHubissa tai paikallisesti, fetcher säilyttää muokkaukset

Formaatti:
{
  "tiedotteet": [
    {
      "date": "2026-10-09",
      "title": "Otsikko",
      "message": "Viesti...",
      "type": "info" // info, success, warning, error
    }
  ],
  "fetched_at": "...",
  "version": "..."
}

Käyttö: python tiedotteet_fetcher.py
GitHub Actions ei tarvitse ajaa tätä, mutta se varmistaa että tiedosto on olemassa.
"""
import json
import pathlib
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [BASE.parent / "data", BASE / "data", BASE, pathlib.Path.cwd() / "data"]
DATA_DIR = None
for c in CANDIDATES:
    if c.exists() and ((c / "tiedotteet.json").exists() or c.name == "data"):
        DATA_DIR = c if c.name == "data" else c
        break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT = {
    "tiedotteet": [
        {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "title": "Tervetuloa!",
            "message": "Tämä on Luoma-ahon Frisbeegolfradan tiedotepalsta. Voit muokata tätä tiedostoa data/tiedotteet.json",
            "type": "info"
        }
    ],
    "version": "V30 - Tiedotteet manuaalinen"
}

def main():
    print("=== tiedotteet_fetcher.py V30 - manuaalinen ===")
    print(f"DATA_DIR={DATA_DIR}")
    p = DATA_DIR / "tiedotteet.json"
    if not p.exists():
        print(f"Ei löydy {p}, luodaan default")
        out = DEFAULT.copy()
        out["fetched_at"] = datetime.now(timezone.utc).isoformat()
        p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK: luotu {p}")
    else:
        print(f"Löytyy {p}, tarkistetaan formaatti")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if "tiedotteet" not in data:
                print("  Puuttuu tiedotteet kenttä, lisätään")
                data["tiedotteet"] = DEFAULT["tiedotteet"]
            # päivitä fetched_at mutta älä ylikirjoita sisältöä
            data["fetched_at"] = datetime.now(timezone.utc).isoformat()
            if "version" not in data:
                data["version"] = DEFAULT["version"]
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"OK: {len(data.get('tiedotteet',[]))} tiedotetta, säilytetty muokkaukset")
        except Exception as e:
            print(f"FAIL: {e}, luodaan varmuuskopio ja default")
            try:
                backup = DATA_DIR / f"tiedotteet_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"  Backup {backup}")
            except:
                pass
            out = DEFAULT.copy()
            out["fetched_at"] = datetime.now(timezone.utc).isoformat()
            p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
