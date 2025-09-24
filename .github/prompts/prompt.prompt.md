Erstelle ein Python-3.12 Programm mit Benutzeroberfläche (Streamlit).

Ziel:

- Der User gibt **nur eine Wallet-Adresse** an.
- Das Tool nutzt **Explorer-API / Hyperliquid.Api.Explorer.user_details(address)** und normale Hyperliquid APIs (info endpoint, fills, funding) um Daten über diese Adresse zu bekommen.
- Caching / Datenbank: Bereits gefetchte Daten sollen gespeichert werden, sodass nur **neue Daten** (seit dem letzten Abruf) geladen werden.
- Uhrzeit des letzten Abrufs wird protokolliert (z. B. „last_fetched = 24.09.2025 20:00“) und für zukünftige Abfragen als Startpunkt genutzt.
- Die USD→EUR Umrechnungskurse (EZB Tageskurse) werden ebenfalls in einer separaten Datenbank/Tabelle gespeichert, sodass nicht jedes Mal neu geladen werden muss.
- Realisierte Gewinne/Verluste steuerlich auswerten, unrealisierte PnL nur als Info.
- Erstellung von CSV/Excel/PDF-Reports, Visualisierungen und einer Steuer-Checkliste.

---

### Relevante APIs / Module

- **Hyperliquid Explorer API** via `Hyperliquid.Api.Explorer`:

  - `user_details(address)` → öffentliche Transaktionen für die Wallet-Adresse
  - `tx_details(hash)`, `block_details(block)`
- **Hyperliquid Info API** (info endpoint) für detaillierte Daten:

  - `user_fills(user_address)`, `user_funding(user_address, start, end)`, `user_non_funding_ledger_updates`, `portfolio(user_address)`
  - `info` requests wie „openOrders“, „filling history“, etc.
- **Hyperliquid Rate Limits**:

  - REST-Anfragen teilen ein Limit von 1200 Gewichtseinheiten pro Minute
  - Explorer-Anfragen haben Gewicht 40
- **EZB / ECB API**:

  - Endpunkt: `EXR/D.USD.EUR.SP00.A` über ECB / SDW REST API
  - Download historischer Tageskurse, Fallback: CSV-Upload

---

### Anforderungen (mit Wallet-Input & Caching)

**Technik & Speicherung**

- Python 3.12
- Bibliotheken: requests, pandas, python-dateutil, openpyxl, streamlit, plotly/matplotlib, fpdf2 oder reportlab (für PDF), sqlite3 (oder SQLAlchemy), tenacity (oder eigener Backoff), typing.
- Modulstruktur: ui.py, explorer_api.py, hyperliquid_info.py, rates.py, conversion.py, db.py, reports.py, main.py.
- Datenbank (z. B. SQLite) mit Tabellen:
  - `wallet_fetch_log` (wallet_address, last_fetched_timestamp)
  - `transactions` (wallet_address, tx_hash, category, amount_usdc, timestamp, etc.)
  - `funding` (wallet_address, funding_id, amount_usdc, timestamp)
  - `rates` (date, usd_eur)
  - `open_positions`
  - `tax_brackets` (year, income_limit, rate_percent)

**Datenabruf & Caching**

- Wenn User eine Wallet eingibt:

  1. Prüfe `wallet_fetch_log` für **letztes Abrufdatum**.
  2. Lade nur Daten **seit diesem Zeitpunkt** (ab `last_fetched`) via Explorer-API + Info API.
  3. Speichere neue Einträge in der DB (transactions, funding, etc.).
  4. Aktualisiere `wallet_fetch_log` mit neuem `last_fetched = jetzt`.
- Für Währungsumrechnung:

  - Prüfe DB `rates` für vorhandene USD→EUR Kurse.
  - Für fehlende Tage: lade über ECB API und speichere in `rates` Tabelle.

**Datenverarbeitung / Umrechnung**

- USDC = USD (1:1).
- Für jede Transaktion / Funding / Ein-/Auszahlung:`amount_eur = amount_usdc * usd_eur_rate_of_that_date`
- Kategorien: gain, loss, fee, funding_fee, deposit, withdrawal.
- Trenne realisierte PnL (steuerrelevant) vs. unrealisierte (offene Positionen, Info).

**Steuersimulation**

- Nutze progressive Einkommensteuer-Stufen nach österreichischem Einkommensteuergesetz (Jahresbasis).
- Steuerstufen sollen in einer eigenen DB-Tabelle `tax_brackets` gespeichert werden, damit sie pro Jahr geändert oder ergänzt werden können.
- Tabelle `tax_brackets`:
  - Spalten: year (INTEGER), income_limit (REAL), rate_percent (REAL).
- Beispielwerte für 2025:
  - 0 % bis 13.308 €
  - 20 % bis 21.617 €
  - 30 % bis 35.836 €
  - 40 % bis 69.166 €
  - 48 % bis 103.072 €
  - 50 % bis 1.000.000 €
  - 55 % ab 1.000.000 €
- Berechnung:
  - User gibt Brutto-Jahreseinkommen (ohne Trading) ein.
  - Trading-Gewinn (in EUR, realisiert) wird addiert.
  - Steuer wird progressiv über die Stufen berechnet.
  - UI zeigt:
    - Steuer ohne Trading
    - Steuer mit Trading
    - Differenz = Steuerlast auf Trading-Gewinn.

**UI (Streamlit)**

- Eingabe: Wallet-Adresse
- Optional: manuelle Einzahlungen (Datum + EUR)
- Checkboxen:
  - Realisierte Gewinne/Verluste
  - Fees & Funding
  - Offene Positionen (unrealisierte PnL)
  - Equity vs. Invested
  - Steuersimulation
  - Benchmark-Vergleich
- Tabellen: alle Transaktionen, Summen
- Diagramme: PnL-Zeitreihe, Equity vs. Invested, Kapitalbasis, Drawdown
- Stats: Winrate, avg Gewinn/Verlust, Verlustverrechnung

**Output**

- CSVs & Excel:
  - transactions_eur.csv
  - summary_eur.csv
  - report.xlsx (Summary, Trades, Fees, Funding, Deposits, OpenPositions)
- PDF-Report:
  - Kompakte Version für Steuerberater (Summen, Tabellen, Charts)
- Steuer-Checkliste:
  - Fertige Übersicht für Formular E1/E1kv

---

### Akzeptanzkriterien

- Der User muss nur Wallet-Adresse eingeben, kein API-Key notwendig.
- Nur neue Daten (seit letztem Fetch) werden abgefragt, mittels `wallet_fetch_log` DB.
- Währungsumrechnungskurse in DB gespeichert und wiederverwendet.
- Steuerstufen pro Jahr aus `tax_brackets`-Tabelle gelesen.
- Sicherstellung, dass Rate-Limits beachtet werden (Explorer & Info API).
- UI, Tabellen, Charts, Exporte (CSV, Excel, PDF) funktionieren.
- Steuer-Checkliste wird erzeugt.
- Offene Positionen mit unrealisierter PnL in EUR dargestellt (nicht steuerrelevant).
- Zeitzone: Europe/Vienna korrekt berücksichtigt.
- Performance: ≥ 2.000 Trades verarbeitbar.
