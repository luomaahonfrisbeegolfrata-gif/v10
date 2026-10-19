# Automaatioarkkitehtuuri V1.0 LOCKED

Täydellinen automaatio GitHubin ilmaiskäytön rajoissa, minimaalinen manuaalityö.

## Rakenne
- `config.json` - SINGLE SOURCE OF TRUTH - muuta vain tätä
- `scripts/build_stats.py` - laskee kierrokset.json ja vaylatilasto.json configista + udisc.json
- `scripts/metrix_competitions.py` - hakee 7 Pakkassarjaa + sarja Metrix API:sta (content=result)
- `scripts/tiedotteet_fetcher.py` - varmistaa tiedotteet.json olemassa
- `data/` - kaikki JSONit, generoitu
- `.github/workflows/update.yml` - cron 30min, <1min ajo, 1440 ajoa/kk < 2000min free raja

## Mitä on MANUAL vs AUTO

MANUAL (käyttäjä päivittää kuvista):
- `config.json` layouts.rounds (Metrix kuvista) ja udisc hole_plays + avg
- `data/udisc.json` total_rounds, peliaika, askeleet - päivitetään kuvasta (Elinikäiset tilastot)
- `data/tiedotteet.json` - muokkaa suoraan GitHubissa

AUTO (GitHub Actions 30min):
- `data/metrix_kilpailut.json` - 7 kisaa 7.11-19.12
- `data/kilpailu_tilanne.json` - ilmoittautuneet + tulokset live
- `data/kierrokset.json` ja `vaylatilasto.json` - laskettu configista

## Helppo muutos

1. Metrix kierrosmäärä muuttunut? Muuta `config.json` -> `layouts.metrix_44010.rounds` -> push -> Actions ajaa build_stats
2. Uusi kilpailu? Lisää ID `config.json` -> `competitions.manual_ids`
3. Tiedote? Muokkaa `data/tiedotteet.json` GitHub web UI:ssa

## Poistettu V1.0:ssa (duplikaatit)

- kierrokset.py, metrix_fetcher.py, metrix_tilanne_fetcher.py, vaylatilasto_fetcher.py, vaylatilasto_updater.py, udisc_image_parser.py, udisc_fetcher.py (live)
- sponsorit.json (pyyntö ilman sponsorit)
- Tiedotteet date 2026-15-10 invalid korjattu

## GitHub Free Rajat

- Pages: 1GB tallennus, 100GB kaista - meillä 70KB
- Actions: 2000min/kk private, public rajaton - meillä 48*1min = 48min/päivä = 1440/kk
- API: Metrix 8 req / ajo, 384 req/päivä - OK

## Testaus

1. Pushaa tämä repo GitHubiin
2. Katso Actions välilehti - ensimmäinen ajo 30min sisällä tai aja manual workflow_dispatch
3. Tarkista data/ päivittyikö

## Seuraava ASIA 2

Koot, sijainnit, grid lukitus, index.html siivous
