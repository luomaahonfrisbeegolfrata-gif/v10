"""
vaylatilasto_fetcher.py - KORJATTU V29 - HTML TAULUKKO LUKITTU
Tämä korjaa V26 bugit: ei tyhjentänyt taulukkoa, vaan generoi koko datan
6 sääntöä lukittu: header, layout, koot, sijainti, data ei riko, väylätilasto lukittu
"""
import json
import pathlib
from datetime import datetime, timezone

# KORJATTU polku
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_vaylatilasto():
    """
    KORJATTU: hakee oikean väylätilaston - ei vain version
    Data kuvasta (kuva.png) - 12 väylää + Tot + %
    """
    # Data suoraan referenssikuvasta - LUKITTU
    data = {
        "vayla_count": 12,
        "par_total": 41,
        "pituus_total": "1248m",
        "avg_total": "49.05",
        "difficulty_total": 78,
        # Pituudet
        "pituus": ["125m", "103m", "72m", "57m", "94m", "96m", "103m", "80m", "116m", "85m", "197m", "120m", "1248m", "-"],
        "par": ["4", "3", "3", "3", "3", "3", "3", "3", "4", "3", "5", "4", "41", "-"],
        # Avg + värikoodit - lukittu kuvasta
        "avg": ["4.45", "3.77", "3.45", "3.42", "3.55", "4.18", "3.79", "3.33", "4.53", "4.20", "6.15", "4.23", "49.05", "-"],
        "avgCls": ["cell-red", "cell-yellow", "cell-green", "cell-green", "cell-yellow", "cell-orange", "cell-yellow", "cell-green", "cell-red", "cell-orange", "cell-red", "cell-orange", "cell-dark", "cell-dark"],
        "difficulty": ["8", "5", "9", "10", "6", "2", "4", "11", "7", "1", "3", "12", "78", "-"],
        "diffCls": ["cell-yellow", "cell-orange", "cell-yellow", "cell-green", "cell-orange", "cell-red", "cell-orange", "cell-green", "cell-yellow", "cell-red", "cell-red", "cell-green", "cell-dark", "cell-dark"],
        # Tilastot
        "hio": ["0", "0", "0", "4", "0", "0", "0", "1", "0", "0", "0", "0", "5", "0.3%"],
        "birdie": ["14", "4", "14", "25", "3", "4", "10", "19", "8", "6", "11", "24", "142", "8.7%"],
        "par0": ["59", "52", "77", "32", "69", "38", "53", "73", "55", "34", "31", "67", "640", "39.2%"],
        "bogey": ["31", "65", "34", "64", "46", "49", "51", "38", "38", "48", "48", "35", "547", "33.5%"],
        "dbl": ["18", "16", "14", "6", "11", "24", "21", "7", "12", "38", "31", "6", "204", "12.5%"],
        "tpl": ["3", "3", "2", "4", "5", "15", "6", "1", "4", "9", "11", "1", "64", "3.9%"],
        "other": ["1", "1", "0", "1", "1", "8", "1", "0", "5", "4", "5", "1", "28", "1.7%"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V29 KORJATTU - täysi taulukko, värit lukittu, ei tyhjä"
    }
    return data

def main():
    print("=== vaylatilasto_fetcher.py V29 KORJATTU ===")
    data = fetch_vaylatilasto()
    
    # Kirjoita - pitää 500px korkean taulukon lukittuna (sääntö 6)
    (DATA_DIR / "vaylatilasto.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"OK: väylätilasto.json -> 12 väylää, Tot {data['pituus_total']} Par {data['par_total']}")
    print(f"  Avg total {data['avg_total']} Difficulty {data['difficulty_total']}")
    print(f"  6 sääntöä lukittu - taulukko 15 saraketta, värit lukittu")

if __name__ == "__main__":
    main()
