"""
WM 2026 – WhatsApp Tipp-Erinnerung via Twilio
Läuft täglich um 17:00 Uhr (GitHub Actions)
Sendet Erinnerung an Teilnehmer die Spiele der nächsten 24h noch nicht getippt haben
"""

import os, sys, requests
from datetime import datetime, timezone, timedelta

TWILIO_SID   = os.environ["TWILIO_SID"]
TWILIO_TOKEN = os.environ["TWILIO_TOKEN"]
TWILIO_FROM  = os.environ["TWILIO_WHATSAPP_FROM"]  # z.B. whatsapp:+14155238886
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

PARTICIPANTS = {
    "Oliver":   "+436644507853",
    "Georg":    "+4366488628799",
    "Anna":     "+436641208733",
    "Snezhana": "+436642609949",
    "Esther":   "+4369915077635",
    "Nolan":    "+436641551519",
    "Leonie":   "+436645070155",
}

TIPP_URL = "https://olivervoigt-afk.github.io/WM2026/tipp/"

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def sb_get(path, params=None):
    r = requests.get(f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}", headers=SB_HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def send_whatsapp(to_number, message):
    r = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
        auth=(TWILIO_SID, TWILIO_TOKEN),
        data={
            "From": TWILIO_FROM,
            "To":   f"whatsapp:{to_number}",
            "Body": message,
        },
        timeout=10,
    )
    return r.status_code, r.json()

def main():
    now = datetime.now(timezone.utc)
    in_24h = now + timedelta(hours=24)

    # Spiele der nächsten 24h laden
    matches = sb_get("matches", params=[
        ("select",      "id,home,away,kickoff_utc"),
        ("kickoff_utc", f"gt.{now.isoformat()}"),
        ("kickoff_utc", f"lte.{in_24h.isoformat()}"),
        ("order",       "kickoff_utc"),
    ])

    if not matches:
        print("Keine Spiele in den nächsten 24h.")
        return

    # Alle Tipps für diese Spiele laden
    match_ids = ",".join(str(m["id"]) for m in matches)
    tips = sb_get("tips", params={
        "select":   "match_id,participant",
        "match_id": f"in.({match_ids})",
    })
    tipped = {(t["match_id"], t["participant"]) for t in tips}

    print(f"{len(matches)} Spiel(e) in den nächsten 24h:")
    for m in matches:
        kt = datetime.fromisoformat(m["kickoff_utc"].replace("+00:00","")).replace(tzinfo=timezone.utc)
        kt_de = kt.astimezone(timezone(timedelta(hours=2)))
        print(f"  {kt_de.strftime('%H:%M')} Uhr  {m['home']} – {m['away']}")

    # Fehlende Tipps pro Person ermitteln
    missing_per = {}
    for name in PARTICIPANTS:
        missing = [m for m in matches if (m["id"], name) not in tipped]
        if missing:
            missing_per[name] = missing

    if not missing_per:
        print("Alle haben getippt – keine Nachricht nötig.")
        return

    # Übersicht der Spiele (einmalig)
    spiele_lines = []
    for m in matches:
        kt = datetime.fromisoformat(m["kickoff_utc"].replace("+00:00","")).replace(tzinfo=timezone.utc)
        kt_de = kt.astimezone(timezone(timedelta(hours=2)))
        spiele_lines.append(f"  ⏰ {kt_de.strftime('%H:%M')} Uhr – {m['home']} vs {m['away']}")
    spiele_text = "\n".join(spiele_lines)

    # Pro Person: fehlende Spiele auflisten
    person_lines = []
    for name, ms in missing_per.items():
        spiele = ", ".join(
            f"{datetime.fromisoformat(m['kickoff_utc'].replace('+00:00','')).replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=2))).strftime('%H:%M')} {m['home']}–{m['away']}"
            for m in ms
        )
        person_lines.append(f"  ❌ *{name}*: {spiele}")

    msg = (
        f"⚽ *WM 2026 Tippspiel – Tipp-Übersicht*\n\n"
        f"Folgende Spiele stehen in den nächsten 24h an:\n{spiele_text}\n\n"
        f"Noch nicht getippt:\n" + "\n".join(person_lines) + "\n\n"
        f"Dashboard: {TIPP_URL.replace('tipp/','dashboard/')}"
    )

    status, resp = send_whatsapp(PARTICIPANTS["Oliver"], msg)
    if status in (200, 201):
        print(f"📱 Zusammenfassung an Oliver gesendet ({len(missing_per)} Personen fehlen)")
    else:
        print(f"❌ Fehler: {resp.get('message','')}", file=sys.stderr)

if __name__ == "__main__":
    main()
