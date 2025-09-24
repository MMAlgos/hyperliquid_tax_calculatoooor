📌 Prompt (für Python 3.12 Streamlit-App mit APIs)
Erstelle ein Python-3.12 Programm mit Benutzeroberfläche (Streamlit).

Ziel:
- Lade Hyperliquid-Daten robust (mit Rate-Limit-Schutz).
- Behandle USDC als USD (1:1).
- Beziehe EZB USD→EUR Tageskurse.
- Rechne ALLE realisierten Gewinne/Verluste/Fees/Funding zum Tageskurs in EUR um.
- Erfasse Einzahlungen (EUR).
- Weise unrealisierte PnL offener Positionen in EUR separat aus (Info, nicht steuerrelevant).
- Erstelle CSV/Excel/PDF-Reports, Visualisierungen und eine Steuer-Checkliste.

---

### Relevante APIs

**Hyperliquid API (Trading-Daten)**
- API-Doku: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
- Python SDK: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- Wichtige Endpunkte:
  - `user_fills` → Realisierte Trades inkl. Fees
  - `user_funding` → Funding Payments
  - `open_positions` → Offene Positionen (unrealisierte PnL, Info)
  - `transfers` (optional) → Ein-/Auszahlungen
- Authentifizierung: API-Key / Secret
- Rate-Limit beachten (429 → Retry-After, sonst Exponential Backoff + Jitter).

**EZB Data Portal (USD→EUR Kurse)**
- API-Doku: https://data.ecb.europa.eu/help/api/overview
- Datensatz: `EXR/D.USD.EUR.SP00.A` = USD zu EUR, Tageskurs
- Beispiel-Endpunkt:


https://data.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata&startPeriod=2025-01-01&endPeriod=2025-12-31

- Fallback: CSV-Upload mit Spalten `date, usd_eur`.

---

### Anforderungen

**Technik**
- Python 3.12
- Libraries: requests, pandas, python-dateutil, openpyxl, streamlit, plotly, fpdf2 oder reportlab (für PDF), tqdm, tenacity (oder eigener Backoff), typing.
- Modulstruktur: ui.py, hyperliquid_api.py, rates.py, conversion.py, reports.py, main.py.
- Keys via UI-Eingabefeld oder ENV (HYPERLIQUID_KEY, HYPERLIQUID_SECRET).
- Rate-Limit-Handling: Token Bucket, Retry-After, Backoff + Jitter.
- Caching von API-Antworten (.cache).

**Datenkategorien**
- Realisierte: gain, loss, fee, funding_fee.
- Cash-Flows: deposit (EUR-Einzahlungen), withdrawal.
- Offene Positionen: unrealisierte PnL in EUR (Info).

**Einzahlungen**
- Eingabe im UI oder CSV-Upload.
- Option: „Am Einzahlungstag in USDC getauscht“ → USDC-Wert dokumentieren.

**Berechnung**
- Netto-Trading-Ergebnis (EUR) = (Summe gain − Summe loss) − (Summe fee + Summe funding_fee).
- Funding Fees: jede Buchung zum Tageskurs in EUR; Summen je Tag.
- Offene Positionen: unrealisierte PnL in EUR separat.

---

### UI-Funktionen (Streamlit)

- Uploads: CSV für Trades oder EZB-Rates.
- Eingaben: API-Key/Secret, Zeitraum, Einzahlungen.
- Checkboxen:
- Realisierte Gewinne/Verluste
- Fees & Funding
- Offene Positionen
- Equity vs. Invested
- Steuersimulation
- Benchmark-Vergleich
- Tabellen: Transaktionen in EUR, Summenübersicht.
- Diagramme:
- PnL-Zeitreihe (kumuliert in EUR)
- Equity vs. Invested
- Kapitalbasis-Diagramm
- Drawdown
- Statistiken:
- Winrate
- Durchschnittlicher Gewinn/Verlust
- Verlustverrechnung
- Steuersimulation:
- Eingabe Normales Gehalt
- Ausgabe Steuerlast nach österr. Tarif
- Benchmark:
- Vergleich mit BTC Buy & Hold.

---

### Output

- CSV/Excel:
- transactions_eur.csv
- summary_eur.csv
- report.xlsx (Sheets: Summary, Trades, Fees, Funding, Deposits, OpenPositions)
- PDF-Report:
- Kompakte Version für Steuerberater (Summen, Tabellen, Charts).
- Steuer-Checkliste:
- Fertige Übersicht für Formular E1/E1kv.

---

### Akzeptanzkriterien

- Trennung realisierte (steuerrelevant) und unrealisierte (Info).
- Verlustverrechnung enthalten.
- Steuersimulation nach österr. Tarif korrekt.
- Kapitalbasis- und Drawdown-Diagramme vorhanden.
- Winrate/Statistik berechnet.
- Benchmark-Vergleich integriert.
- Export in CSV, Excel und PDF funktioniert.
- OpenPositions mit Unrealized_PnL_EUR.
- UI performant für ≥ 2.000 Trades.
- Zeitzone Europe/Vienna korrekt.
