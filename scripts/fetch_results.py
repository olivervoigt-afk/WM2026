"""
WM 2026 – Automatische Ergebnisabfrage
Quelle: football-data.org (kostenlose API)
Läuft via GitHub Actions alle 5 Minuten
"""

import os, sys, requests
from datetime import datetime, timezone, timedelta

FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]
SUPABASE_URL     = os.environ["SUPABASE_URL"]
SUPABASE_KEY     = os.environ["SUPABASE_KEY"]

# Englische API-Namen → Deutsche DB-Namen
TEAM_MAP = {
    "Mexico": "Mexiko",
    "South Africa": "Südafrika",
    "Korea Republic": "Südkorea",
    "Czechia": "Tschechien",
    "Czech Republic": "Tschechien",
    "Canada": "Kanada",
    "Bosnia and Herzegovina": "Bosnien-Herz.",
    "USA": "USA",
    "United States": "USA",
    "Qatar": "Katar",
    "Switzerland": "Schweiz",
    "Brazil": "Brasilien",
    "Morocco": "Marokko",
    "Haiti": "Haiti",
    "Scotland": "Schottland",
    "Australia": "Australien",
    "Turkey": "Türkei",
    "Türkiye": "Türkei",
    "Germany": "Deutschland",
    "Curaçao": "Curaçao",
    "Curacao": "Curaçao",
    "Netherlands": "Niederlande",
    "Japan": "Japan",
    "Ivory Coast": "Elfenbeinküste",
    "Côte d'Ivoire": "Elfenbeinküste",
    "Ecuador": "Ecuador",
    "Sweden": "Schweden",
    "Tunisia": "Tunesien",
    "Spain": "Spanien",
    "Cape Verde": "Kap Verde",
    "Belgium": "Belgien",
    "Egypt": "Ägypten",
    "Saudi Arabia": "Saudi-Arabien",
    "Uruguay": "Uruguay",
    "Iran": "Iran",
    "New Zealand": "Neuseeland",
    "France": "Frankreich",
    "Senegal": "Senegal",
    "Iraq": "Irak",
    "Norway": "Norwegen",
    "Argentina": "Argentinien",
    "Algeria": "Algerien",
    "Austria": "Österreich",
    "Jordan": "Jordanien",
    "Portugal": "Portugal",
    "DR Congo": "DR Kongo",
    "Congo DR": "DR Kongo",
    "Democratic Republic of Congo": "DR Kongo",
    "England": "England",
    "Croatia": "Kroatien",
    "Ghana": "Ghana",
    "Panama": "Panama",
    "Uzbekistan": "Usbekistan",
    "Colombia": "Kolumbien",
    "Paraguay": "Paraguay",
    "New Zealand": "Neuseeland",
    "Israel": "Israel",
}


def sb_get(path):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def sb_patch(path, data):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{path}",
        json=data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def fetch_finished_matches():
    r = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches",
        params={"status": "FINISHED"},
        headers={"X-Auth-Token": FOOTBALL_API_KEY},
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("matches", [])


def main():
    now = datetime.now(timezone.utc)

    # Alle unsere Spiele ohne Ergebnis laden
    db_matches = sb_get("matches?select=id,home,away,kickoff_utc,result&order=kickoff_utc")
    open_matches = [m for m in db_matches if not m.get("result")]

    if not open_matches:
        print("Alle Spiele haben bereits ein Ergebnis.")
        return

    # Index: (home_de, away_de) → db match
    db_index = {}
    for m in open_matches:
        # Nur Spiele berücksichtigen die vor >105 min angepfiffen wurden
        kickoff = datetime.fromisoformat(m["kickoff_utc"].replace("+00:00", "+00:00"))
        if kickoff.tzinfo is None:
            kickoff = kickoff.replace(tzinfo=timezone.utc)
        if now - kickoff < timedelta(minutes=105):
            continue
        db_index[(m["home"], m["away"])] = m

    if not db_index:
        print("Keine Spiele bereit für Ergebnisabfrage (noch nicht >105 min nach Anstoß).")
        return

    # Ergebnisse von API holen
    try:
        api_matches = fetch_finished_matches()
    except Exception as e:
        print(f"API-Fehler: {e}", file=sys.stderr)
        sys.exit(1)

    updated = 0
    for api_m in api_matches:
        score = api_m.get("score", {}).get("fullTime", {})
        home_goals = score.get("home")
        away_goals = score.get("away")
        if home_goals is None or away_goals is None:
            continue

        home_en = api_m.get("homeTeam", {}).get("name", "")
        away_en = api_m.get("awayTeam", {}).get("name", "")
        home_de = TEAM_MAP.get(home_en)
        away_de = TEAM_MAP.get(away_en)

        if not home_de or not away_de:
            print(f"Kein Mapping für: {home_en} / {away_en}")
            continue

        db_m = db_index.get((home_de, away_de))
        if not db_m:
            continue  # Spiel nicht in unserer DB oder schon mit Ergebnis

        result = f"{home_goals}:{away_goals}"
        print(f"✓ Eintrage: {home_de} – {away_de} = {result}")
        sb_patch(f"matches?id=eq.{db_m['id']}", {"result": result})
        updated += 1

    print(f"\n{updated} Ergebnis(se) eingetragen.")


if __name__ == "__main__":
    main()
