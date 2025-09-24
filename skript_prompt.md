Erstelle ein Python-3.12 Programm mit Benutzeroberfläche (Streamlit).

Ziel:
- Lade Hyperliquid-Daten robust (mit Rate-Limit-Schutz).
- Behandle USDC als USD (1:1).
- Beziehe EZB USD→EUR Tageskurse.
- Rechne ALLE realisierten Gewinne/Verluste/Fees/Funding zum Tageskurs in EUR um.
- Erfasse Einzahlungen (EUR).
- Weise unrealisierte PnL offener Positionen in EUR separat aus (Info, nicht steuerrelevant).
- Erstelle CSV/Excel-Reports und Visualisierungen.

---

### Anforderungen

**Technik**
- Python 3.12
- Libraries: requests, pandas, python-dateutil, openpyxl, streamlit, plotly oder matplotlib, tqdm, tenacity (oder eigener Backoff), typing.
- Saubere Modulstruktur: ui.py, hyperliquid_api.py, rates.py, conversion.py, reports.py, main.py.
- Konfig via UI (kein CLI). Keys via Eingabefeld oder ENV (HYPERLIQUID_KEY, HYPERLIQUID_SECRET).

**Hyperliquid-API**
- Endpunkte (Platzhalter, an echte API-Doku anpassen):
  - Fills/Executions (realisierte Trades + Fees pro Fill)
  - Funding Payments (alle paar Stunden)
  - Open Positions (mit size, entry price, mark price)
  - (Optional) Transfers/Deposits/Withdrawals
- Pagination sauber verarbeiten.
- Rate-Limit beachten:
  - HTTP 429: Retry-After respektieren; sonst exponentieller Backoff mit Jitter.
  - Retries auch bei 5xx/Timeouts.
  - Globale Request-Budgetierung (Token Bucket, z. B. 5–10 req/s).
- Caching (lokal JSON in .cache) für wiederholte Abrufe.

**Zeiten & Kurse**
- Alle Timestamps → nach Europe/Vienna konvertieren.
- EZB USD→EUR Tageskurs laden (ECB SDW) oder CSV-Upload.
- USDC = USD (1:1).
- Umrechnung: amount_eur = amount_usdc * usd_eur_rate_of_day.

**Datenkategorien**
- Realisierte: gain, loss, fee, funding_fee.
- Cash-Flows: deposit (EUR-Einzahlungen), withdrawal.
- Offene Positionen: separat (nicht steuerrelevant); berechne unrealisierte PnL in USDC und EUR zum Tageskurs.

**Einzahlungen**
- Variante A: Nutzer gibt im UI EUR-Einzahlungen (Datum + Betrag) an.
- Variante B: CSV-Upload (`timestamp, eur_amount`).
- Option: „Am Einzahlungstag in USDC getauscht“ → dokumentiere USDC-Wert.

**Berechnung**
- Realisierter Netto-Trading-Erfolg (EUR) = (Summe gain − Summe loss) − (Summe fee + Summe funding_fee).
- Funding Fees: jede Buchung zum Tageskurs umrechnen; zusätzlich Aggregat pro Datum berechnen.
- Offene Positionen: unrealisierte PnL in EUR getrennt ausweisen.

---

### UI-Funktionen (Streamlit)

- Uploads:
  - CSV für Trades oder EZB-Rates.
- Eingaben:
  - API-Key/Secret
  - Zeitraum (Start/Enddatum)
  - Einzahlungen (manuell oder CSV)
- Checkboxen zum Anhaken:
  - Realisierte Gewinne/Verluste anzeigen
  - Fees und Funding einbeziehen
  - Offene Positionen anzeigen
  - Equity vs. Invested anzeigen
- Tabellen-Ansichten:
  - Alle Transaktionen in EUR
  - Summenübersicht
- Diagramme:
  - PnL-Zeitreihe (kumuliert in EUR)
  - Equity vs. Invested (Linienchart)
- Export-Buttons:
  - CSV und Excel (mehrere Sheets: Summary, Trades, Fees, Funding, Deposits, OpenPositions)

---

### Output (CSV + Excel)

- transactions_eur.csv – alle normalisierten Transaktionen
- summary_eur.csv – Summen je Kategorie
- report.xlsx – Sheets:
  - Summary (alle Kennzahlen + unrealisierte PnL + Hinweise)
  - Trades
  - Fees
  - Funding (inkl. Pivot je Datum)
  - Deposits
  - OpenPositions (mit Unrealized_PnL_EUR)
- Excel-Formatierung: Header fett, Tausendertrennzeichen, 2 Dezimalstellen, Auto-Filter.

---

### Akzeptanzkriterien

- Trennung realisierte (steuerrelevant) und unrealisierte (Info).
- Nutzt EZB-Tageskurse je Transaktionsdatum; USDC=USD.
- Erstellt report.xlsx, transactions_eur.csv, summary_eur.csv.
- Sheet OpenPositions mit Unrealized_PnL_EUR vorhanden.
- Rate-Limit-sicher (429-Handling, Backoff, Jitter).
- Zeitzone Europe/Vienna korrekt angewendet.
- UI performant auch für ≥ 2.000 Trades.
