"""
WM 2026 – Automatische Ergebnisabfrage + Livescores
Quelle: football-data.org (kostenlose API)
Läuft via GitHub Actions jede Minute
"""

import os, sys, requests
from datetime import datetime, timezone, timedelta

FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]
SUPABASE_URL     = os.environ["SUPABASE_URL"]
SUPABASE_KEY     = os.environ["SUPABASE_KEY"]

TEAM_MAP = {
    "Mexico": "Mexiko",
    "South Africa": "Südafrika",
    "Korea Republic": "Südkorea",
    "Czechia": "Tschechien",
    "Czech Republic": "Tschechien",
    "Canada": "Kanada",
    "Bosnia and Herzegovina": "Bosnien-Herz.",
    "Bosnia-Herzegovina": "Bosnien-Herz.",
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
}

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_get(path):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{path}", headers=SB_HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def sb_patch(path, data):
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{path}", json=data, headers=SB_HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_api_matches(*statuses):
    params = {"status": ",".join(statuses)}
    r = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches",
        params=params,
        headers={"X-Auth-Token": FOOTBALL_API_KEY},
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("matches", [])

def map_teams(api_m):
    home_en = api_m.get("homeTeam", {}).get("name", "")
    away_en = api_m.get("awayTeam", {}).get("name", "")
    return TEAM_MAP.get(home_en), TEAM_MAP.get(away_en)

def main():
    now = datetime.now(timezone.utc)

    # Alle DB-Spiele laden
    db_matches = sb_get("matches?select=id,home,away,kickoff_utc,result,live_score,live_status&order=kickoff_utc")
    db_index = {(m["home"], m["away"]): m for m in db_matches}

    # --- 0. KO-TEAMS AUTOMATISCH BEFÜLLEN (wenn noch '?') ---
    placeholder_matches = [m for m in db_matches if m["home"] == "?" and m["away"] == "?"]
    if placeholder_matches:
        try:
            ko_api = fetch_api_matches("SCHEDULED", "TIMED")
            ko_stages = {"LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "THIRD_PLACE", "FINAL"}
            # Index: kickoff_utc → DB-Match
            kt_index = {m["kickoff_utc"][:16]: m for m in placeholder_matches}
            for api_m in ko_api:
                if api_m.get("stage") not in ko_stages:
                    continue
                home_en = api_m.get("homeTeam", {}).get("name")
                away_en = api_m.get("awayTeam", {}).get("name")
                if not home_en or not away_en:
                    continue
                home_de = TEAM_MAP.get(home_en, home_en)
                away_de = TEAM_MAP.get(away_en, away_en)
                kt = api_m["utcDate"][:16]
                db_m = kt_index.get(kt)
                if db_m:
                    print(f"🔄 KO-Teams: {home_de} – {away_de} ({kt} UTC)")
                    sb_patch(f"matches?id=eq.{db_m['id']}", {"home": home_de, "away": away_de})
                    # Index aktualisieren damit spätere Schritte das Spiel finden
                    db_index[(home_de, away_de)] = {**db_m, "home": home_de, "away": away_de}
                    del db_index[("?", "?")]
        except Exception as e:
            print(f"Hinweis KO-Teams: {e}", file=sys.stderr)

    # --- 1. LAUFENDE SPIELE (IN_PLAY, HALF_TIME, PAUSED, EXTRA_TIME, PENALTY) ---
    try:
        live_api = fetch_api_matches("LIVE")
    except Exception as e:
        print(f"API-Fehler (live): {e}", file=sys.stderr)
        live_api = []

    live_keys = set()
    for api_m in live_api:
        home_de, away_de = map_teams(api_m)
        if not home_de or not away_de:
            continue
        db_m = db_index.get((home_de, away_de))
        if not db_m:
            continue

        score = api_m.get("score", {})
        # Nutze fullTime-Score (wird während des Spiels laufend aktualisiert)
        ft = score.get("fullTime", {})
        h, a = ft.get("home"), ft.get("away")
        if h is None or a is None:
            continue

        status = api_m.get("status", "")
        minute = api_m.get("minute")

        live_score = f"{h}:{a}"
        if status in ("HALF_TIME", "PAUSED"):
            live_status = "HZ"
        elif status == "EXTRA_TIME":
            live_status = "Verlängerung"
        elif status == "PENALTY":
            live_status = "Elfmeter"
        else:
            live_status = "Live"

        key = (home_de, away_de)
        live_keys.add(key)

        # Nur updaten wenn sich was geändert hat
        if db_m.get("live_score") != live_score or db_m.get("live_status") != live_status:
            print(f"🔴 Live: {home_de} – {away_de} {live_score} ({live_status})")
            sb_patch(f"matches?id=eq.{db_m['id']}", {
                "live_score": live_score,
                "live_status": live_status,
            })

    # --- 2. BEENDETE SPIELE ---
    try:
        finished_api = fetch_api_matches("FINISHED")
    except Exception as e:
        print(f"API-Fehler (finished): {e}", file=sys.stderr)
        finished_api = []

    updated = 0
    for api_m in finished_api:
        home_de, away_de = map_teams(api_m)
        if not home_de or not away_de:
            continue
        db_m = db_index.get((home_de, away_de))
        if not db_m:
            continue

        ft = api_m.get("score", {}).get("fullTime", {})
        h, a = ft.get("home"), ft.get("away")
        if h is None or a is None:
            continue

        result = f"{h}:{a}"
        patch = {}
        if not db_m.get("result"):
            patch["result"] = result
        # Live-Felder leeren wenn Spiel beendet
        if db_m.get("live_score") or db_m.get("live_status"):
            patch["live_score"] = None
            patch["live_status"] = None

        if patch:
            print(f"✓ Ergebnis: {home_de} – {away_de} = {result}")
            sb_patch(f"matches?id=eq.{db_m['id']}", patch)
            updated += 1

    # --- 3. Live-Felder leeren für Spiele die nicht mehr live sind ---
    for (home_de, away_de), db_m in db_index.items():
        if db_m.get("live_score") and (home_de, away_de) not in live_keys:
            # Nur leeren wenn Spiel nicht in der FINISHED-Liste ist (verhindert Race condition)
            if not db_m.get("result"):
                pass  # Noch nicht fertig, Geduld
            else:
                print(f"🧹 Live-Daten leeren: {home_de} – {away_de}")
                sb_patch(f"matches?id=eq.{db_m['id']}", {"live_score": None, "live_status": None})

    print(f"\n{len(live_api)} live, {updated} Ergebnis(se) neu eingetragen.")

if __name__ == "__main__":
    main()
