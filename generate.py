#!/usr/bin/env python3
"""
Punteirolos 8.0 — Generador automático de estadísticas
Ejecuta: python generate.py
Genera: index.html con todos los datos actualizados
"""

import json
import time
import base64
import os
import urllib.request
import urllib.error
from pathlib import Path

LEAGUE_ID = 854
FPL_BASE = "https://fantasy.premierleague.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://fantasy.premierleague.com/",
}

def fpl_get(path, retries=3):
    url = FPL_BASE + path
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"  Intento {attempt+1} fallido para {path}: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    raise Exception(f"No se pudo obtener {path} después de {retries} intentos")

def fetch_all():
    print("📡 Obteniendo clasificación...")
    standings_data = fpl_get(f"/leagues-h2h/{LEAGUE_ID}/standings/")
    teams = standings_data["standings"]["results"]
    league_name = standings_data["league"]["name"]
    print(f"  Liga: {league_name} — {len(teams)} equipos")

    print("📡 Obteniendo partidos H2H...")
    all_matches = []
    page = 1
    while True:
        data = fpl_get(f"/leagues-h2h-matches/league/{LEAGUE_ID}/?page={page}")
        results = data.get("results", [])
        # Solo partidos con puntos (jugados)
        played = [m for m in results if m["entry_1_points"] + m["entry_2_points"] > 0]
        all_matches.extend(played)
        print(f"  Página {page}: {len(played)} partidos jugados")
        if not data.get("has_next"):
            break
        page += 1
        time.sleep(0.5)

    print(f"  Total partidos: {len(all_matches)}")

    print("📡 Obteniendo historiales y picks...")
    histories = []
    captain_data = {}  # entry_id -> {gw: captain_element_id}
    
    for i, team in enumerate(teams):
        entry_id = team["entry"]
        print(f"  [{i+1}/{len(teams)}] {team['entry_name']}...")
        
        # History (GW scores, chips)
        try:
            hist = fpl_get(f"/entry/{entry_id}/history/")
            histories.append(hist)
        except:
            histories.append(None)
            print(f"    ⚠ No se pudo obtener historial")
        
        # Picks por jornada (capitán)
        caps = {}
        current = (histories[-1] or {}).get("current", [])
        for gw_data in current:
            gw = gw_data["event"]
            try:
                picks = fpl_get(f"/entry/{entry_id}/event/{gw}/picks/")
                cap = next((p for p in picks.get("picks", []) if p.get("is_captain")), None)
                if cap:
                    caps[gw] = cap["element"]
            except:
                pass
            time.sleep(0.2)
        captain_data[entry_id] = caps
        time.sleep(0.5)

    return league_name, teams, all_matches, histories, captain_data

def build_teams_js(teams):
    lines = []
    for t in teams:
        lines.append(
            f'  {{e:{t["entry"]},n:{json.dumps(t["entry_name"])},p:{json.dumps(t["player_name"])},'
            f'r:{t["rank"]},w:{t["matches_won"]},d:{t["matches_drawn"]},l:{t["matches_lost"]},'
            f'pts:{t["points_for"]}}}'
        )
    return "const TEAMS = [\n" + ",\n".join(lines) + "\n];"

def build_matches_js(matches):
    lines = []
    for m in matches:
        e1 = m["entry_1_entry"]
        s1 = m["entry_1_points"]
        e2 = m["entry_2_entry"]
        s2 = m["entry_2_points"]
        gw = m["event"]
        lines.append(f"  [{e1},{s1},{e2},{s2},{gw}]")
    return "const MATCHES = [\n" + ",\n".join(lines) + "\n];"

def build_chips_js(teams, histories):
    chip_data = {}
    for i, team in enumerate(teams):
        hist = histories[i] or {}
        chips = hist.get("chips", [])
        chip_data[team["entry"]] = [{"name": c["name"], "event": c["event"]} for c in chips]
    return f"const CHIPS = {json.dumps(chip_data)};"

def build_captains_js(captain_data):
    return f"const CAPTAINS = {json.dumps(captain_data)};"

def build_gw_scores_js(teams, histories):
    """GW scores per team for charts"""
    gw_scores = {}
    for i, team in enumerate(teams):
        hist = histories[i] or {}
        current = hist.get("current", [])
        gw_scores[str(team["entry"])] = {str(g["event"]): g["points"] for g in current}
    return f"const GW_SCORES = {json.dumps(gw_scores)};"

def get_splash_b64():
    """Load splash image if exists"""
    for name in ["splash.png", "splash.jpg", "campeon.png"]:
        path = Path(__file__).parent / name
        if path.exists():
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

def generate_html(league_name, teams_js, matches_js, chips_js, captains_js, gw_scores_js, splash_b64, last_updated):
    """Read template and inject data"""
    template_path = Path(__file__).parent / "template.html"
    html = template_path.read_text(encoding="utf-8")
    
    # Inject data
    html = html.replace("%%LEAGUE_NAME%%", league_name)
    html = html.replace("%%LAST_UPDATED%%", last_updated)
    html = html.replace("%%TEAMS_JS%%", teams_js)
    html = html.replace("%%MATCHES_JS%%", matches_js)
    html = html.replace("%%CHIPS_JS%%", chips_js)
    html = html.replace("%%CAPTAINS_JS%%", captains_js)
    html = html.replace("%%GW_SCORES_JS%%", gw_scores_js)
    html = html.replace("%%SPLASH_B64%%", splash_b64)
    
    return html

def main():
    print("🚀 Punteirolos — Generador de estadísticas")
    print("=" * 50)
    
    from datetime import datetime
    last_updated = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Fetch data
    league_name, teams, matches, histories, captains = fetch_all()
    
    # Build JS blocks
    print("\n⚙️  Construyendo datos...")
    teams_js = build_teams_js(teams)
    matches_js = build_matches_js(matches)
    chips_js = build_chips_js(teams, histories)
    captains_js = build_captains_js(captains)
    gw_scores_js = build_gw_scores_js(teams, histories)
    splash_b64 = get_splash_b64()
    
    print(f"  Equipos: {len(teams)}")
    print(f"  Partidos: {len(matches)}")
    print(f"  Splash: {'Sí' if splash_b64 else 'No (pon splash.png en la carpeta)'}")
    
    # Generate HTML
    print("\n📄 Generando HTML...")
    html = generate_html(league_name, teams_js, matches_js, chips_js, captains_js, gw_scores_js, splash_b64, last_updated)
    
    out_path = Path(__file__).parent / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  ✅ Guardado en: {out_path} ({len(html)//1024} KB)")
    print("\n🎉 ¡Listo! Abre index.html en el navegador.")

if __name__ == "__main__":
    main()
