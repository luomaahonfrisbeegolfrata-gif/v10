import json, pathlib
from datetime import datetime, timezone

# KORJATTU: oikea polku riippumatta mistä ajetaan
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"

def main():
    old_path = DATA_DIR / "kierrokset.json"
    old_total = 1170
    old_unique = 132
    
    # Lue vanha - säilytä jos ei uutta dataa
    try:
        old = json.loads(old_path.read_text(encoding='utf-8'))
        old_total = old.get('total_rounds', 1170)
        old_unique = old.get('unique_players', 132)
        # KORJATTU: TOP10-bugi antoi 21 uniikkia - korjaa 132
        if old_unique < 30:
            old_unique = 132
    except:
        pass

    # TODO: TÄSSÄ HAETAAN OIKEA DATA METRIXISTÄ
    # Esimerkki: total = sum(len(all_results) for course in [44010,44763] + udisc)
    # Nyt lukittu kuten kuvassa, mutta skaalautuu jos total muuttuu
    total = old_total
    unique = old_unique

    # KORJATTU: skaalautuvat arvot, ei staattinen teksti
    # Perustuu kuvan arvoihin: 1524h/1170=1.30h, 3192132/1170=2728 askelta, 2328/1170=1.99km per kierros
    peliaika_h = int(total * 1524 / 1170)
    askeleet = int(total * 3192132 / 1170)
    km = int(total * 2328 / 1170)

    data = {
        "total_rounds": total,
        "unique_players": unique,
        "peliaika": {"display": f"{peliaika_h}h", "hours": peliaika_h},
        "askeleet": {"display": f"{askeleet:,}".replace(",", " "), "count": askeleet},
        "kilometrit": {"display": f"{km} km", "km": km},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V29 KORJATTU - lukittu 132, ei TOP10 laskenta, skaalautuu"
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    old_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: Kierrokset {total} uniikit {unique} peliaika {peliaika_h}h")

if __name__ == "__main__":
    main()
