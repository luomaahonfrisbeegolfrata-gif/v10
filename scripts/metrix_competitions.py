#!/usr/bin/env python3
"""metrix_competitions.py - kilpailulista ja tilanne Metrixin API:sta.

Korvaa: metrix_tilanne_fetcher.py (joka ei hakenut tuloksia lainkaan eikä tallentanut päivämääriä).
Kirjoittaa: data/metrix_kilpailut.json, data/kilpailu_tilanne.json, data/status.json
- API: https://discgolfmetrix.com/api.php?content=result&id=<kilpailu-id>   (TARKISTA Metrixin ehdot ja vastausrakenne ensimmäisellä ajolla)
- epäonnistuessa vanhaa dataa ei ylikirjoiteta (kilpailu merkitään stale)
- kisat joiden tulos on vielä tyhjä näytetään 'N ilmoittautunutta', ei kuvitteellista sijoitusta

Käyttö: python scripts/metrix_competitions.py [data-kansio]
"""
import json
import pathlib
import re
import sys
import time
from datetime import datetime, timedelta, timezone

try:
    import requests
except ImportError:
    requests = None
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

HERE = pathlib.Path(__file__).resolve().parent
def find_config_comp():
    for cand in [HERE / "config.json", HERE.parent / "config.json", pathlib.Path.cwd() / "config.json", pathlib.Path.cwd() / "scripts" / "config.json"]:
        if cand.exists():
            return cand
    return HERE / "config.json"
def find_data_comp():
    if len(sys.argv) > 1:
        return pathlib.Path(sys.argv[1])
    if HERE.name == "scripts":
        return HERE.parent / "data"
    return HERE / "data" if (HERE / "data").exists() else HERE.parent / "data"
CFG_PATH = find_config_comp()
DATA = find_data_comp()
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))["competitions"]
BASE = "https://discgolfmetrix.com"
API = f"{BASE}/api.php"
HEADERS = {"User-Agent": CFG.get("user_agent", "luoma-aho-stats/1.0")}
FMT_FI = "%d.%m.%Y %H:%M"
FMTS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d.%m.%Y %H:%M", "%d.%m.%Y")
HEARTBEAT = timedelta(hours=3)


def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save(name, obj):
    p = DATA / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def now_fi():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Helsinki")).replace(tzinfo=None)
    except Exception:
        return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2)


def parse_dt(s):
    s = (s or "").strip()
    for f in FMTS:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    return None


def api_result(cid):
    r = requests.get(API, params={"content": "result", "id": cid}, headers=HEADERS, timeout=20)
    r.raise_for_status()
    j = r.json()
    comp = j.get("Competition") if isinstance(j, dict) else None
    if not isinstance(comp, dict):
        raise ValueError(f"odottamaton vastaus: {str(j)[:120]}")
    return comp


def discover(known):
    """Etsii uusia kilpailulinkkejä kurssisivuilta (valinnainen, kaatuessaan hiljainen)."""
    if requests is None or BeautifulSoup is None:
        return []
    found = []
    for course in CFG.get("discover_courses", []):
        try:
            r = requests.get(f"{BASE}/course/{course}", headers=HEADERS, timeout=20)
            r.raise_for_status()
            for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True):
                m = re.fullmatch(r"(?:https://discgolfmetrix\.com)?/(\d{6,9})/?", a["href"])
                if m and m.group(1) not in known and m.group(1) not in found:
                    found.append(m.group(1))
        except Exception as e:
            print(f"  discover {course} epäonnistui: {e}")
    return found[:20]


def start_of(comp):
    d = str(comp.get("Date") or "").strip()
    t = str(comp.get("Time") or "").strip()
    if t and len(d) == 10:
        d = f"{d} {t}"
    return parse_dt(d)


def plus_str(diff):
    try:
        d = int(diff)
    except (TypeError, ValueError):
        return ""
    return "E" if d == 0 else f"{d:+d}"


def parse_results(comp):
    rows = []
    for p in comp.get("Results") or []:
        if not isinstance(p, dict):
            continue
        name = str(p.get("Name") or "").strip()
        if not name:
            continue
        try:
            total = int(p.get("Sum"))
        except (TypeError, ValueError):
            total = 0
        rows.append({"name": name, "total": total, "plus": plus_str(p.get("Diff"))})
    scored = sorted((r for r in rows if r["total"] > 0), key=lambda r: (r["total"], r["name"]))
    ranked, last, rank = [], None, 0
    for i, r in enumerate(scored, 1):
        if r["total"] != last:
            rank, last = i, r["total"]
        ranked.append({"rank": rank, **r})
    return len(rows), ranked


def main():
    if requests is None:
        sys.exit("requests puuttuu: pip install requests beautifulsoup4")
    now = now_fi()
    old_list = (load(DATA / "metrix_kilpailut.json", {}) or {}).get("kilpailut", [])
    old_rec = {str(k.get("id")): k for k in old_list}
    old_tilanne = {str(c.get("id")): c for c in (load(DATA / "kilpailu_tilanne.json", {}) or {}).get("competitions", [])}

    manual = [str(i) for i in CFG["manual_ids"]]
    found = discover(set(manual))
    series = {str(k): [str(x) for x in v] for k, v in CFG.get("series", {}).items()}
    course = CFG.get("default_course", {"id": "44010", "name": "Luoma-aho"})

    recs, tilanne, times, ok = {}, {}, {}, 0
    for cid in manual + found:
        try:
            comp = api_result(cid)
        except Exception as e:
            print(f"  {cid}: API epäonnistui ({e})")
            if cid in old_rec:
                recs[cid] = {**old_rec[cid], "stale": True}
                if cid in old_tilanne:
                    tilanne[cid] = old_tilanne[cid]
                times[cid] = parse_dt(old_rec[cid].get("date"))
            time.sleep(0.5)
            continue
        ok += 1
        start = start_of(comp)
        if cid in found and (start is None or start < now - timedelta(days=1) or start > now + timedelta(days=200)):
            time.sleep(0.5)
            continue
        registered, ranked = parse_results(comp)
        name = str(comp.get("Name") or (old_rec.get(cid) or {}).get("name") or f"Kilpailu {cid}").strip()
        times[cid] = start
        end = start + timedelta(hours=6) if start else None
        if start and now >= start:
            reg = "Käynnissä" if now < end else "Päättynyt"
        else:
            reg = (old_rec.get(cid) or {}).get("reg") or "Tulossa"
        ctype = "Sarja" if cid in series else "Finaali" if re.search(r"FINAA|FINALE", name.upper()) else "Viikkokisa"
        recs[cid] = {
            "date": start.strftime(FMT_FI) if start else "", "name": name,
            "course": course["id"], "courseName": course["name"],
            "competitionId": cid, "id": cid, "type": ctype, "url": f"{BASE}/{cid}",
            "reg": reg, "registration": reg, "players": registered, "active": True,
        }
        tilanne[cid] = {
            "id": cid, "name": name, "date": recs[cid]["date"], "course": course["name"], "courseId": course["id"],
            "url": recs[cid]["url"], "status": reg, "registered": registered, "results": ranked[:30],
            "isLive": reg == "Käynnissä", "isUpcoming": reg not in ("Käynnissä", "Päättynyt"),
        }
        time.sleep(0.5)

    if ok == 0:
        print("Kaikki API-kutsut epäonnistuivat - vanhat tiedostot jätetään ennalleen")
        sys.exit(1)

    # sarjat: päivämääräväli lapsikisoista, päättyy kun viimeinen lapsi on päättynyt
    ends = {}
    for sid, kids in series.items():
        if sid not in recs:
            continue
        ds = [times[k] for k in kids if times.get(k)]
        if ds:
            lo, hi = min(ds), max(ds)
            recs[sid]["date"] = f"{lo.strftime('%d.%m')} - {hi.strftime('%d.%m.%Y')}"
            recs[sid]["isSeries"] = True
            ends[sid] = hi + timedelta(hours=24)
            recs[sid]["players"] = max(recs[sid]["players"], max((recs[k]["players"] for k in kids if k in recs), default=0))
            sreg = "Päättynyt" if now > hi + timedelta(hours=6) else "Käynnissä" if now >= lo else (old_rec.get(sid) or {}).get("reg") or "Avoinna"
            recs[sid]["reg"] = recs[sid]["registration"] = sreg
            if sid in tilanne:
                tilanne[sid]["date"] = recs[sid]["date"]
                tilanne[sid]["status"] = sreg
                tilanne[sid]["isLive"] = sreg == "Käynnissä"
                tilanne[sid]["isUpcoming"] = now < lo

    def finished(cid):
        end = ends.get(cid) or (times[cid] + timedelta(hours=30) if times.get(cid) else None)
        return bool(end and now > end)

    keep = [c for c in recs if not finished(c)]
    keep.sort(key=lambda c: (c not in series, times.get(c) or datetime.max, c))
    kilpailut = [recs[c] for c in keep]
    t_list = [tilanne[c] for c in keep if c in tilanne]

    live = [t for t in t_list if t["isLive"]]
    nxt = [t for t in t_list if t["isUpcoming"] and t["id"] not in series]
    current = (live or nxt or t_list or [None])[0]

    stamp = now.strftime("%d.%m.%Y %H:%M")
    save("metrix_kilpailut.json", {"kilpailut": kilpailut, "updated": stamp, "source": "Metrix API content=result", "version": "V2.0"})
    save("kilpailu_tilanne.json", {"competitions": t_list, "current": current, "activeId": current["id"] if current else None,
                                   "updated": stamp, "source": "Metrix API content=result", "version": "V3.0"})

    st = load(DATA / "status.json", {}) or {}
    last = parse_dt((st.get("generated_at") or "").replace("T", " ")[:19])
    utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if not last or utc - last > HEARTBEAT:
        save("status.json", {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "competitions_ok": ok, "competitions_total": len(manual + found)})
    print(f"OK: {len(kilpailut)} kilpailua listalla, {ok} API-kutsua onnistui")


if __name__ == "__main__":
    main()
