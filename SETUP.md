# Setup-Checkliste (Morgen früh, vor 15:30 MESZ)

Stand der Maschine (geprüft 2026-09-01): Python 3.12.10, Node 24, git 2.49, Claude Code 2.1.257 vorhanden. **Fehlt:** `uv`/`uvx` (für den MCP-Server), Alpaca CLI, `alpaca-py`.

> **Stand 3. September, 00:40 MESZ:** Wettbewerbskonto ist PA31SEVJV9P9 (brandneu, 100.000 $, Optionsstufe 3); das Pilotkonto PA314NYH4H7G vom 2. September ist archiviert (`state/pilot_PA314NYH4H7G_2026-09-02/`).
> **Stand 2. September, 09:15 MESZ:** Schritte 1 bis 4 erledigt (Paper-Konto PA314NYH4H7G aktiv, Keys in `.env`, venv unter `.venv`, MCP-Server ohne uv direkt aus der venv registriert und verbunden). Offen: Alpaca-CLI (Schritt 5).

## 1. Alpaca-Account und Paper-Konto (musst du selbst machen, ca. 15 min)

1. Registrieren über den Hackathon-Link: https://alpaca.markets/?utm_source=website&utm_medium=event&utm_campaign=lablab_hackathon
2. Im Dashboard oben auf **Paper Trading** wechseln. Das Standard-Paper-Konto startet mit 100.000 $.
   - Pflicht: Das Konto für die Abgabe muss **neu und nur für den Hackathon** sein, Startguthaben **exakt 100.000 $**. Falls du zum Testen Trades machst, vorher ein zweites Paper-Konto anlegen oder das Konto **vor dem ersten echten Agenten-Trade** per "Reset" auf 100.000 $ zurücksetzen. Am besten: heute ein Test-Konto, morgen früh ein frisches Abgabe-Konto.
3. **Paper Account ID** notieren (steht im Dashboard unter dem Kontonamen; wird für die Abgabe gebraucht).
4. Unter Paper Trading **API Keys generieren**: `API Key ID` und `Secret Key`. Der Secret wird nur einmal angezeigt.
5. Prüfen, ob im Paper-Konto **Options Trading Level 3** aktiv ist (Account -> Configuration -> Options). Level 3 brauchen wir für Spreads und Iron Condors. In Paper ist Optionshandel laut Doku standardmäßig aktiv.

## 2. Secrets lokal ablegen

Datei `C:\jannis\projects\hackathons\Alpaca_AI_Trading\.env` anlegen (wird nie committet):

```
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
ALPACA_PAPER_TRADE=true
ALPACA_ACCOUNT_ID=...
FEATHERLESS_API_KEY=...
```

## 3. Python-Umgebung (5 min)

```powershell
cd C:\jannis\projects\hackathons\Alpaca_AI_Trading
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install alpaca-py python-dotenv anthropic uv
```

`uv` liefert auch `uvx.exe`, das der MCP-Server braucht. Test: `uvx --version`.

## 4. Alpaca MCP-Server in Claude Code registrieren (5 min)

Mit aktivierter venv, echte Keys einsetzen:

```powershell
claude mcp add alpaca --scope user --transport stdio uvx alpaca-mcp-server --env ALPACA_API_KEY=PK... --env ALPACA_SECRET_KEY=... --env ALPACA_PAPER_TRADE=true
```

Dann in Claude Code `/mcp` eingeben und prüfen, dass `alpaca` verbunden ist. Der Server bringt 65 Tools mit, darunter `get_option_chain`, `get_option_snapshot` (Greeks, IV) und `place_option_order` (Multi-Leg).

## 5. Alpaca CLI installieren (5 min)

Windows-Binary v0.0.14 vom 28.08.2026:
https://github.com/alpacahq/cli/releases/download/v0.0.14/cli_0.0.14_windows_amd64.zip

```powershell
New-Item -ItemType Directory -Force C:\tools\alpaca
Expand-Archive -Path $env:USERPROFILE\Downloads\cli_0.0.14_windows_amd64.zip -DestinationPath C:\tools\alpaca
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\tools\alpaca", "User")
```

Neues Terminal öffnen, dann:

```powershell
alpaca version
alpaca doctor
$env:ALPACA_API_KEY="PK..."; $env:ALPACA_SECRET_KEY="..."
alpaca account get
alpaca clock
```

Paper ist Standard. Die CLI gibt JSON aus, kennt `--dry-run` und `--jq`. Wir nutzen sie für Cron-artige Monitoring-Jobs und den Abgleich.

## 6. Featherless-Credits (5 min)

Anleitung des Hackathons: https://lablab.ai/tech/featherless (25 $ Credits pro Teilnehmer, first come first served). Key in `.env` als `FEATHERLESS_API_KEY`.

## 7. Funktionstest (2 min)

```powershell
alpaca data option chain SPY --jq '.[0:3]'
```

Wenn hier Kontrakte kommen, sind Daten, Auth und Optionszugang in Ordnung.

## Zeitfenster

| Was | Wann (MESZ) |
|---|---|
| US-Markt offen | 15:30 bis 22:00 |
| Broadcom (AVGO), Snowflake, HPE Earnings | Mi 2.9. nach Börsenschluss |
| Ciena Earnings | Do 3.9. vor Börsenöffnung |
| Zscaler, Samsara, Lululemon, DocuSign Earnings | Do 3.9. nach Börsenschluss |
| Abgabe-Deadline | Fr 4.9. 17:00 |
