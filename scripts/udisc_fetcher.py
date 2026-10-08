"""
udisc_fetcher.py - KORJATTU V29
UDisc TOP10 - oikeat UDisc käyttäjät, ei Metrix nimiä
Korjattu: rankit 1-10 peräkkäin, nimet oikein, polku korjattu
6 sääntöä lukittu
"""
import json
import pathlib
from datetime import datetime, timezone

# KORJATTU polku
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# KORJATTU: rankit 1-10, nimet kuten kuvassa ja edellisessä V26 mutta ilman typo
# Aiemmassa V26 bugit: rank 4 kahdesti, rank 5 puuttuu, @mattiasss (3 s), @itkonenjere vs @tikonenjere, @peetu7 vs @neetu7, @tommivluoma vs @tommivuoma
UDISC_TOP_CORRECTED = [
    {"rank": 1, "name": "@kantanen8", "total": 35, "plus_minus": "-6"},
    {"rank": 2, "name": "@valkoparta", "total": 36, "plus_minus": "-5"},
    {"rank": 3, "name": "@mattiass", "total": 36, "plus_minus": "-5"},  # korjattu 3 s -> 2 s
    {"rank": 4, "name": "@dashyy", "total": 38, "plus_minus": "-3"},
    {"rank": 5, "name": "@tikonenjere", "total": 38, "plus_minus": "-3"},  # korjattu @itkonenjere -> @tikonenjere, rank 4->5
    {"rank": 6, "name": "@neetu7", "total": 39, "plus_minus": "-2"},  # korjattu @peetu7 -> @neetu7
    {"rank": 7, "name": "@taspak", "total": 42, "plus_minus": "+1"},
    {"rank": 8, "name": "@adusti", "total": 43, "plus_minus": "+2"},
    {"rank": 9, "name": "@tommivuoma", "total": 47, "plus_minus": "+6"},  # korjattu @tommivluoma -> @tommivuoma
    {"rank": 10, "name": "@attekolis", "total": 48, "plus_minus": "+7"},
]

def main():
    data = {
        "course": "UDISC Luoma-aho 12 väylää Par 41",
        "par": 41,
        "top10": UDISC_TOP_CORRECTED,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "version": "V29 KORJATTU - UDisc oikeat nimet, rankit 1-10, ei Metrix sekoitus"
    }
    
    # Kirjoita vain yksi tiedosto jota frontti käyttää (sääntö 5: data ei riko)
    (DATA_DIR / "udisc.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # Älä kirjoita duplikaattia udisc_top10.json ellei tarvitse
    # (DATA_DIR / "udisc_top10.json").write_text(...) - poistettu, turha
    
    print(f"OK: UDisc V29 - {len(UDISC_TOP_CORRECTED)} pelaajaa, rankit 1-10, nimet korjattu")
    for r in UDISC_TOP_CORRECTED:
        print(f"  {r['rank']}. {r['name']} {r['total']} {r['plus_minus']}")

if __name__ == "__main__":
    main()
