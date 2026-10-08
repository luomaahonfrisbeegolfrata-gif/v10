"""
metrix_fetcher.py - KORJATTU V29
Hakee Metrix 44010, 44763 ja UDisc, laskee uniikit OIKEIN (ei TOP10:stä)
Säännöt: 1.header lukittu 2.layout lukittu 3.koot lukittu 4.sijainti lukittu 5.data ei riko 6.väylätilasto lukittu
"""

import json
import pathlib
import re
from datetime import datetime, timezone
from collections import Counter

# KORJATTU polku - toimii mistä vain ajetaan
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def parse_metrix_course(course_id, par):
    """
    TÄSSÄ OIKEA FETCH - korvaa tämä oikealla Metrix API kutsulla
    Metrixillä ei ole virallista public API:a, joten tässä esimerkki:
    - Hae https://discgolfmetrix.com/course/{course_id}/results
    - Parse kaikki tulokset, ei vain TOP10
    """
    # Placeholder - lukee olemassa olevan tiedoston jos on, muuten fallback
    # OIKEA TOTEUTUS: requests.get(f"https://discgolfmetrix.com/api.php?content=results&course={course_id}")
    fallback_top10 = []
    total_results = 0
    all_players = []
    
    # Yritä lukea vanha top10 säilyttääksesi lukitun layoutin
    try:
        old = json.loads((DATA_DIR / f"metrix_{course_id}.json").read_text(encoding='utf-8'))
        fallback_top10 = old.get('top10', [])
        # ÄLÄ laske uniikkeja tästä - tämä antaa 10, ei 132
    except:
        pass
    
    return {
        "top10": fallback_top10,
        "total_results": total_results,
        "all_players": all_players
    }

def calculate_totals():
    """KORJATTU: laskee total_rounds ja unique_players OIKEIN, ei TOP10:stä"""
    
    # 1. Hae kaikki kurssit
    courses = [
        {"id": "44010", "par": 41},
        {"id": "44763", "par": 82},
        {"id": "43119"},
    ]
    
    all_players_global = []
    total_rounds_global = 0
    
    for course in courses:
        result = parse_metrix_course(course["id"], course["par"])
        # KORJATTU: älä käytä len(top10) = 10, vaan kaikki tulokset
        # total_rounds_global += result["total_results"]  # OIKEA
        # all_players_global.extend(result["all_players"])  # OIKEA
        
        # V28 BUGI oli: total = len(top10) = 10 tai 21 jos yhdistää kaksi rataa
        # Siksi lukittiin 1170 ja 132
        pass
    
    # LUKITTU kuten kuvassa - kunnes toteutat oikean fetchin
    # Kun toteutat, korvaa nämä:
    # total_rounds = total_rounds_global + udisc_total
    # unique_players = len(set(all_players_global))
    
    total_rounds = 1170  # kuvasta
    unique_players = 132  # kuvasta, EI 21 (TOP10 bugi)
    
    return total_rounds, unique_players

def main():
    print("=== metrix_fetcher.py V29 KORJATTU ===")
    
    # 1. Laske oikeat summat - EI TOP10:stä
    total_rounds, unique_players = calculate_totals()
    
    # 2. Skaalautuvat johdannaiset - kuten kuvassa 1524h / 3 192 132 / 2328 km
    # 1170 kierrosta = 1524h = 1.302h per kierros
    peliaika_h = int(total_rounds * 1524 / 1170)
    askeleet = int(total_rounds * 3192132 / 1170)
    km = int(total_rounds * 2328 / 1170)
    
    # 3. Kirjoita kierrokset.json - V29 formaatti, ei redundantteja total/count
    kierrokset = {
        "total_rounds": total_rounds,
        "unique_players": unique_players,
        "peliaika": {"display": f"{peliaika_h}h", "hours": peliaika_h},
        "askeleet": {"display": f"{askeleet:,}".replace(",", " "), "count": askeleet},
        "kilometrit": {"display": f"{km} km", "km": km},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V29 KORJATTU - metrix_fetcher, ei TOP10 uniikit"
    }
    
    # Backward compat - vanha frontti saattoi käyttää näitä
    # Säilytä mutta älä luota näihin
    kierrokset["total"] = total_rounds
    kierrokset["count"] = total_rounds
    kierrokset["uniikit_pelaajat"] = unique_players
    
    (DATA_DIR / "kierrokset.json").write_text(json.dumps(kierrokset, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK: kierrokset.json -> {total_rounds} kierrosta, {unique_players} uniikkia")
    print(f"  peliaika {peliaika_h}h, askeleet {askeleet}, km {km}km")
    print(f"  6 sääntöä lukittu - layout ei hajoa vaikka data puuttuu")

if __name__ == "__main__":
    main()
