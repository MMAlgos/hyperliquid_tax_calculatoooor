# 🇦🇹 Hyperliquid Tax Calculator - Österreich# 🇦🇹 Hyperliquid Tax Calculator - Österreich# 🇦🇹 Austrian Tax Report Generator for Hyperliquid Trading



**Automatische Steuerberechnung für Hyperliquid Trading nach österreichischem Steuerrecht 2025**



---**Automatische Steuerberechnung für Hyperliquid Trading nach österreichischem Steuerrecht 2025**## ✅ COMPLETE SYSTEM - VERSION 2.0



## 📋 Überblick



Dieses Programm berechnet automatisch Ihre österreichische Steuerlast aus Hyperliquid-Trading und kombiniert diese mit Ihrem Lohn-Einkommen. Es nutzt die offiziellen ECB-Wechselkurse für EUR/USD-Konvertierung und erstellt alle benötigten Unterlagen für Ihre Steuererklärung.---### 🎯 **Features Implemented**



### ✨ Hauptfunktionen



| Feature | Beschreibung |## 📋 Überblick1. **ECB API Integration** - Real-time EUR/USD conversion with 101 cached exchange rates

|---------|-------------|

| 🇪🇺 **EUR-Konvertierung** | Automatische Umrechnung mit ECB-Tageskursen (207+ gecachte Kurse) |2. **Austrian Tax Law 2025** - Complete progressive tax brackets with corrected loss treatment

| 💰 **Monatliches Einkommen** | CSV-basierte Eingabe für monatsgenaue Gehaltsangaben |

| 📊 **Vollständige Datenerfassung** | Trades, Funding, Deposits, Positionen - alles automatisch |Dieses Programm berechnet automatisch Ihre österreichische Steuerlast aus Hyperliquid-Trading und kombiniert diese mit Ihrem Lohn-Einkommen. Es nutzt die offiziellen ECB-Wechselkurse für EUR/USD-Konvertierung und erstellt alle benötigten Unterlagen für Ihre Steuererklärung.3. **Separated Tax Display** - Shows Lohn-only vs Trading vs Combined tax calculations

| 🇦🇹 **Österreichisches Steuerrecht 2025** | Korrekte progressive Steuersätze (0%-50%) |

| 📄 **PDF-Steuerreport** | Professioneller Report mit allen Details für Finanzamt |4. **Tax Form Guidance** - Generates detailed PDF instructions for Austrian Steuererklärung

| 📦 **ZIP-Export** | Alle Dateien organisiert in einem Paket |

| ➕ **Manuelle Ergänzungen** | CSV-System für Trades/Deposits von anderen Plattformen |### ✨ Hauptfunktionen5. **User Input System** - Interactive input for wallet, yearly income, and tax year



---6. **Organized Output** - Separate folders for CSV, PDF, and ZIP files



## 🚀 Installation & Start| Feature | Beschreibung |7. **PDF Reports** - Comprehensive Austrian tax reports with proper terminology



### 1. Abhängigkeiten installieren|---------|-------------|



```bash| 🇪🇺 **EUR-Konvertierung** | Automatische Umrechnung mit ECB-Tageskursen (207+ gecachte Kurse) |### � **Quick Start**

pip install -r requirements.txt

```| 💰 **Monatliches Einkommen** | CSV-basierte Eingabe für monatsgenaue Gehaltsangaben |



### 2. Programm starten| 📊 **Vollständige Datenerfassung** | Trades, Funding, Deposits, Positionen - alles automatisch |```bash



```bash| 🇦🇹 **Österreichisches Steuerrecht 2025** | Korrekte progressive Steuersätze (0%-50%) |# Install dependencies

python hyperliquid_fetcher.py

```| 📄 **PDF-Steuerreport** | Professioneller Report mit allen Details für Finanzamt |pip install -r requirements.txt



### 3. Eingaben tätigen| 📦 **ZIP-Export** | Alle Dateien organisiert in einem Paket |



Das Programm fragt Sie nach:| ➕ **Manuelle Ergänzungen** | CSV-System für Trades/Deposits von anderen Plattformen |# Run the system



- **Wallet-Adresse**: Ihre Hyperliquid Wallet (z.B. `0xAbCd123456...`)python hyperliquid_fetcher.py

- **Steuerjahr**: Jahr für Berechnung (z.B. `2025`)

---```

Ihr Einkommen geben Sie in der CSV-Datei `manual_input/monthly_income.csv` ein (wird automatisch erstellt).



---

## 🚀 Installation & Start### 📋 **What You'll Enter**

## 💰 Monatliches Einkommen (CSV-System)



### So funktioniert's:

### 1. Abhängigkeiten installieren- **Wallet Address**: Your Hyperliquid wallet address (0x...)

1. Beim ersten Start wird automatisch `manual_input/monthly_income.csv` erstellt

2. Öffnen Sie die Datei und tragen Sie Ihr **monatliches Bruttogehalt** ein- **Lohn-Einkommen**: Your yearly salary income in EUR (e.g., 50000)

3. Sie können für jeden Monat einen anderen Betrag eintragen

```bash- **Tax Year**: The year for tax calculation (e.g., 2024)

### Beispiel `monthly_income.csv`:

pip install -r requirements.txt

```csv

monat,jahr,brutto_gehalt,enabled```### 🀽� **Generated Files**

Januar,2025,3500,1

Februar,2025,3500,1

März,2025,4200,1

April,2025,3500,1### 2. Programm starten#### CSV Files (Raw Data)

Mai,2025,3500,1

Juni,2025,3500,1

Juli,2025,3500,1

August,2025,3500,1```bash- `trades_WALLET_YEAR.csv` - All trading transactions

September,2025,3500,1

Oktober,2025,3500,1python hyperliquid_fetcher.py- `funding_WALLET_YEAR.csv` - Funding payments/receipts

November,2025,3500,1

Dezember,2025,5000,1```- `positions_WALLET_YEAR.csv` - Position history

```



**Vorteile:**

- ✅ Präzise bei Gehaltserhöhungen### 3. Eingaben tätigen#### PDF Reports

- ✅ Bonuszahlungen in bestimmten Monaten

- ✅ Unbezahlter Urlaub (Monat auf `enabled=0` setzen)

- ✅ Teilzeit mit wechselndem Gehalt

Das Programm fragt Sie nach:- `Austrian_Tax_Report_WALLET_YEAR.pdf` - Complete tax analysis

**Dezimalformat:**

- Komma: `3500,50` ✅- `Ueberweisung_Finanzamt_AT_WALLET_YEAR.pdf` - **Tax form instructions**

- Punkt: `3500.50` ✅

- Beide funktionieren!- **Wallet-Adresse**: Ihre Hyperliquid Wallet (z.B. `0xAbC123...`)



---- **Steuerjahr**: Jahr für Berechnung (z.B. `2025`)#### ZIP Archive



## ➕ Manuelle Ergänzungen (andere Plattformen)



Falls Sie auch auf **anderen Börsen** (z.B. Binance, Coinbase) gehandelt haben, können Sie diese Daten manuell hinzufügen:Ihr Einkommen geben Sie in der CSV-Datei `manual_input/monthly_income.csv` ein (wird automatisch erstellt).- Complete package with all files for tax submission



### 📂 CSV-Dateien im `manual_input/` Ordner:



| Datei | Zweck | Beispiel |---### 🇦🇹 **Austrian Tax Form Instructions**

|-------|-------|----------|

| `manual_deposits.csv` | Einzahlungen von anderen Plattformen | Binance → Bank: 5000 EUR |

| `manual_trades.csv` | Trades von anderen Plattformen | Verkauf ASTER auf Binance |

| `monthly_income.csv` | Monatliches Bruttogehalt | 12× Monatsgehälter |## 💰 Monatliches Einkommen (CSV-System)The system generates a **Tax Form Guidance PDF** that shows exactly:



### Beispiel `manual_trades.csv`:



```csv### So funktioniert's:1. **Which forms to use**: E1 (main) + E1kv (capital gains)

date,coin,side,size,price,currency,enabled

2025-10-14,ASTER,sell,18772,1.37,USD,12. **Where to enter trading profits**: Specific field references

```

1. Beim ersten Start wird automatisch `manual_input/monthly_income.csv` erstellt3. **How much to transfer**: Exact amount for Finanzamt

**Automatische Features:**

- ✅ EUR↔USD Konvertierung am Handelstag2. Öffnen Sie die Datei und tragen Sie Ihr **monatliches Bruttogehalt** ein4. **Step-by-step process**: From FinanzOnline login to submission

- ✅ Enable/Disable mit `enabled` Spalte (1=aktiv, 0=deaktiviert)

- ✅ Bidirektionale Währungsunterstützung3. Sie können für jeden Monat einen anderen Betrag eintragen



---### 💡 **Key Austrian Tax Rules Applied**



## 📊 Was wird berechnet?### Beispiel `monthly_income.csv`:



### 🔍 Erfasste Daten von Hyperliquid- ✅ **Losses don't reduce salary income** (corrected implementation)



| Kategorie | Details |```csv- ✅ **Only positive trading results are taxable**

|-----------|---------|

| **Trades** | Alle Käufe/Verkäufe mit Preisen, Fees, realisiertem PnL |monat,jahr,brutto_gehalt,enabled- ✅ **Progressive tax brackets 2025** (0% to 55%)

| **Funding** | Funding Paid (abzugsfähig), Funding Received (Ertrag) |

| **Deposits/Withdrawals** | Ein- und Auszahlungen (nicht steuerpflichtig) |Januar,2025,3500,1- ✅ **FIFO methodology** for position calculations

| **Open Positions** | Aktuelle Positionen (unrealisiert = Info only) |

| **Fees** | Trading Fees (steuerlich abzugsfähig) |Februar,2025,3500,1- ✅ **Proper German terminology** throughout



### 💸 SteuerberechnungMärz,2025,4200,1



```April,2025,3500,1### 🔧 **Technical Details**

🇦🇹 Österreichische Steuerprogression 2025:

────────────────────────────────────────────Mai,2025,3500,1

bis €13,308  →  0%   (Freibetrag)

bis €21,617  →  20%Juni,2025,3500,1- **Currency Conversion**: ECB Statistical Data API with daily rates

bis €35,836  →  30%

bis €69,166  →  40%Juli,2025,3500,1- **Tax Calculations**: Mathematically verified Austrian progressive system

bis €103,416 →  48%

ab  €103,416 →  50%August,2025,3500,1- **Data Processing**: FIFO-based position tracking

```

September,2025,3500,1- **PDF Generation**: ReportLab with professional formatting

**Wichtig:**

- ✅ Trading-Gewinne werden zum Lohn-Einkommen addiertOktober,2025,3500,1- **Error Handling**: Robust validation and error reporting

- ✅ Trading-Verluste mindern NICHT das Lohn-Einkommen (Deckelung auf 0€)

- ✅ Nur realisierte Gewinne/Verluste sind steuerrelevantNovember,2025,3500,1

- ✅ Funding Received = steuerpflichtiger Ertrag

- ✅ Funding Paid + Trading Fees = abzugsfähige KostenDezember,2025,5000,1### ⚖️ **Legal Compliance**



---```



## 📦 Generierte DateienThis system implements Austrian tax law as of 2025. Always consult with a qualified Austrian tax advisor (Steuerberater) for official tax advice.



Nach dem Durchlauf erhalten Sie einen **ZIP-Ordner** mit folgendem Inhalt:**Vorteile:**



```- ✅ Präzise bei Gehaltserhöhungen---

HL_AT_2025_0xAbCd12_20251026_1234/

├── 01_Summary/- ✅ Bonuszahlungen in bestimmten Monaten

│   └── summary.csv                    # Zusammenfassung

├── 02_Trades/- ✅ Unbezahlter Urlaub (Monat auf `enabled=0` setzen)## 🎯 **EXAMPLE TAX CALCULATION OUTPUT**

│   ├── trades.csv                     # Alle Trades mit EUR-Konvertierung

│   └── fees.csv                       # Alle Trading Fees- ✅ Teilzeit mit wechselndem Gehalt

├── 03_Funding/

│   └── funding.csv                    # Funding Paid/Received```

├── 04_Transfers/

│   └── deposits_withdrawals.csv       # Ein-/Auszahlungen**Dezimalformat:**🇦🇹 ÖSTERREICHISCHE STEUERBERECHNUNG - ERGEBNISSE

└── 05_PDF_Report/

    └── HL_tax_report_AT_*.pdf         # 📄 STEUER-PDF für Finanzamt- Komma: `3500,50` ✅════════════════════════════════════════════════════════════════════════════════

```

- Punkt: `3500.50` ✅💰 Lohn-Einkommen (vom Arbeitgeber): €50,000.00

### 📄 PDF-Steuerreport enthält

- Beide funktionieren!📊 Trading-Ergebnis (Hyperliquid): €2,532.98

- ✅ Zusammenfassung: Lohn + Trading-Gewinn

- ✅ Detaillierte Steuertabelle nach Progressionsstufen💸 Steuer nur auf Lohn: €7,950.00

- ✅ Trading-Kosten Aufschlüsselung (Fees + Funding Paid)

- ✅ Alle Trades mit Datum, Coin, Gewinn/Verlust in EUR---📈 Steuer mit Trading: €8,963.19

- ✅ Funding-Historie

- ✅ Anleitung für Steuererklärung (welches Formular, welches Feld)💡 Zusätzliche Steuer durch Trading: €1,013.19



---## ➕ Manuelle Ergänzungen (andere Plattformen)



## 🔧 Technische DetailsFÜR STEUERERKLÄRUNG:



### APIs & DatenquellenFalls Sie auch auf **anderen Börsen** (z.B. Binance, Coinbase) gehandelt haben, können Sie diese Daten manuell hinzufügen:📋 Trading-Gewinn (E1kv eintragen): €2,532.98



| Service | Zweck |💳 Zusätzlich zu überweisen: €1,013.19

|---------|-------|

| **Hyperliquid API** | Trade-Daten, Funding, Positionen |### 📂 CSV-Dateien im `manual_input/` Ordner:```

| **ECB Statistical Data API** | Offizielle EUR/USD Wechselkurse |



### Berechnungsmethoden

| Datei | Zweck | Beispiel |---

- **FIFO (First-In-First-Out)**: Position Tracking

- **Tagesgenauer Wechselkurs**: Jeder Trade wird mit ECB-Kurs vom Handelstag konvertiert|-------|-------|----------|

- **Progressive Steuer**: Stufenweise Berechnung nach österr. Einkommensteuergesetz

| `manual_deposits.csv` | Einzahlungen von anderen Plattformen | Binance → Bank: 5000 EUR |**🎉 Ready for Austrian Steuererklärung 2025!**

### Fehlerbehandlung

| `manual_trades.csv` | Trades von anderen Plattformen | Verkauf ASTER auf Binance |

- ✅ Pagination für >2000 Trades (automatisch)

- ✅ Retry-Logik bei API-Timeouts| `monthly_income.csv` | Monatliches Bruttogehalt | 12× Monatsgehälter |A comprehensive Python application that fetches all your Hyperliquid trading data including trades, funding history, deposits/withdrawals, and open positions.

- ✅ Währungs-Parsing: Komma UND Punkt als Dezimalzeichen

- ✅ Datenvalidierung mit aussagekräftigen Fehlermeldungen



---### Beispiel `manual_trades.csv`:## Features ✨



## 🎯 Beispiel: Vollständiger Ablauf



### 1️⃣ Programm starten```csv- **Complete Trade History**: Fetches all your trade fills with detailed information



```bashdate,coin,side,size,price,currency,enabled- **Funding History**: Retrieves funding payments/receipts for all positions

python hyperliquid_fetcher.py

```2025-10-14,ASTER,sell,18772,1.37,USD,1- **Transfer History**: Gets deposit and withdrawal records



### 2️⃣ Eingaben```- **Open Positions**: Shows current positions with unrealized PnL, leverage, and liquidation prices



```- **Data Export**: Saves data in CSV, JSON, and text summary formats

Wallet-Adresse: 0xYourWalletAddressHere

Steuerjahr: 2025**Automatische Features:**- **Clean Summaries**: Generates readable reports with key metrics

```

- ✅ EUR↔USD Konvertierung am Handelstag

### 3️⃣ Einkommen in CSV eintragen

- ✅ Enable/Disable mit `enabled` Spalte (1=aktiv, 0=deaktiviert)## Quick Start 🚀

Öffne `manual_input/monthly_income.csv`:

- ✅ Bidirektionale Währungsunterstützung

```csv

monat,jahr,brutto_gehalt,enabled1. **Install Dependencies**:

Januar,2025,3080,1

Februar,2025,3080,1---

...

Dezember,2025,3080,1   ```bash

```

## 📊 Was wird berechnet?   pip install -r requirements.txt

### 4️⃣ Ergebnis

   ```

```

═══════════════════════════════════════════════════════════════### 🔍 Erfasste Daten von Hyperliquid:2. **Run the Script**:

🇦🇹 ÖSTERREICHISCHE STEUERKALKULATION 2025

═══════════════════════════════════════════════════════════════

💰 Lohn-Einkommen: €36,960.00

📊 Trading-Gewinn (steuerlich): €1,234.56| Kategorie | Details |   ```bash

🔢 Gesamteinkommen (steuerpflichtig): €38,194.56

|-----------|---------|   python hyperliquid_fetcher.py

💸 Steuer nur auf Lohn: €6,377.10

💸 Zusatzsteuer durch Trading: €493.82| **Trades** | Alle Käufe/Verkäufe mit Preisen, Fees, realisiertem PnL |   ```

💰 Steuer gesamt: €6,870.92

| **Funding** | Funding Paid (abzugsfähig), Funding Received (Ertrag) |

────────────────────────────────────────────────────────────────

📋 FÜR STEUERERKLÄRUNG:| **Deposits/Withdrawals** | Ein- und Auszahlungen (nicht steuerpflichtig) |The script is pre-configured with your wallet address: `0x343434238412742847278429874d2`

💰 Trading-Gewinn (E1kv eintragen): €1,234.56

💸 Zusätzlich zu überweisen: €493.82| **Open Positions** | Aktuelle Positionen (unrealisiert = Info only) |

```

| **Fees** | Trading Fees (steuerlich abzugsfähig) |## What You Get 📈

---



## ⚖️ Rechtliche Hinweise

### 💸 Steuerberechnung:### Console Output

⚠️ **Wichtig**: Dieses Programm ist eine **Berechnungshilfe** und ersetzt keine professionelle Steuerberatung.



- Konsultieren Sie einen **österreichischen Steuerberater** für offizielle Beratung

- Die Berechnungen basieren auf dem **Einkommensteuergesetz 2025**```- Real-time fetching progress

- Das Programm wurde nach bestem Wissen entwickelt, aber **ohne Gewähr**

- Verwenden Sie die generierten Unterlagen als **Grundlage für Ihre Steuererklärung**🇦🇹 Österreichische Steuerprogression 2025:- Complete trading summary with:



---────────────────────────────────────────────  - Account value and available balance



## 📞 Support & Entwicklungbis €13,308  →  0%   (Freibetrag)  - Open positions with PnL and leverage



**Version**: 3.0 (2025)  bis €21,617  →  20%  - Trading statistics (volume, fees, realized PnL)

**Sprache**: Python 3.7+  

**Lizenz**: MIT  bis €35,836  →  30%  - Top traded assets



### Anforderungenbis €69,166  →  40%  - Funding history summary



```bis €103,416 →  48%  - Deposit/withdrawal totals

requests >= 2.31.0

pandas >= 2.0.0ab  €103,416 →  50%

reportlab >= 4.0.0

``````### Files Generated



---



## 🎉 Features auf einen Blick**Wichtig:**- `hyperliquid_trades_[timestamp].csv` - Detailed trade history



✅ Vollautomatische Datenerfassung von Hyperliquid  - ✅ Trading-Gewinne werden zum Lohn-Einkommen addiert- `hyperliquid_funding_[timestamp].csv` - Funding payments/receipts

✅ Monatsgenaue Einkommenseingabe via CSV  

✅ Manuelle Ergänzungen für andere Plattformen  - ✅ Trading-Verluste mindern NICHT das Lohn-Einkommen (Deckelung auf 0€)- `hyperliquid_transfers_[timestamp].csv` - Deposits and withdrawals

✅ EUR/USD Konvertierung mit offiziellen ECB-Kursen  

✅ Österreichisches Steuerrecht 2025 korrekt implementiert  - ✅ Nur realisierte Gewinne/Verluste sind steuerrelevant- `hyperliquid_summary_[timestamp].txt` - Human-readable summary report

✅ PDF-Report für Finanzamt  

✅ ZIP-Export aller Unterlagen  - ✅ Funding Received = steuerpflichtiger Ertrag- `hyperliquid_raw_data_[timestamp].json` - Complete raw API responses

✅ Komma UND Punkt als Dezimaltrennzeichen  

✅ Enable/Disable System für alle CSV-Einträge  - ✅ Funding Paid + Trading Fees = abzugsfähige Kosten



**Bereit für Ihre österreichische Steuererklärung 2025!** 🇦🇹## Data Included 📋


---

### Trade Data

## 📦 Generierte Dateien

- Timestamp, coin, side (buy/sell), size, price

Nach dem Durchlauf erhalten Sie einen **ZIP-Ordner** mit folgendem Inhalt:- Direction (Open Long, Close Short, etc.)

- Closed PnL, fees, starting position

```- Transaction hashes and order IDs

HL_AT_2025_0xABC123_20251026_1234/

├── 01_Summary/### Funding Data

│   └── summary.csv                    # Zusammenfassung

├── 02_Trades/- Funding rates and payments per position

│   ├── trades.csv                     # Alle Trades mit EUR-Konvertierung- Position sizes at funding time

│   └── fees.csv                       # Alle Trading Fees- Timestamps and transaction hashes

├── 03_Funding/

│   └── funding.csv                    # Funding Paid/Received### Transfer Data

├── 04_Transfers/

│   └── deposits_withdrawals.csv       # Ein-/Auszahlungen- Deposits, withdrawals, internal transfers

└── 05_PDF_Report/- Amounts and timestamps

    └── HL_tax_report_AT_*.pdf         # 📄 STEUER-PDF für Finanzamt- Transaction details

```

### Account State

### 📄 PDF-Steuerreport enthält:

- Current account value and margin usage

- ✅ Zusammenfassung: Lohn + Trading-Gewinn- Open positions with:

- ✅ Detaillierte Steuertabelle nach Progressionsstufen  - Position size and entry price

- ✅ Trading-Kosten Aufschlüsselung (Fees + Funding Paid)  - Unrealized PnL and ROE%

- ✅ Alle Trades mit Datum, Coin, Gewinn/Verlust in EUR  - Margin used and max leverage

- ✅ Funding-Historie  - Liquidation prices

- ✅ Anleitung für Steuererklärung (welches Formular, welches Feld)

## API Endpoints Used 🔌

---

- `userFills` - Trade history (max 2000 recent fills)

## 🔧 Technische Details- `userFunding` - Funding payments/receipts

- `userNonFundingLedgerUpdates` - Deposits/withdrawals

### APIs & Datenquellen:- `clearinghouseState` - Current positions and account info

- `frontendOpenOrders` - Open orders

| Service | Zweck |

|---------|-------|## Configuration 🛠️

| **Hyperliquid API** | Trade-Daten, Funding, Positionen |

| **ECB Statistical Data API** | Offizielle EUR/USD Wechselkurse |To use with a different wallet address, modify the `wallet_address` variable in the `main()` function:



### Berechnungsmethoden:```python

wallet_address = "0xYourWalletAddressHere"

- **FIFO (First-In-First-Out)**: Position Tracking```

- **Tagesgenauer Wechselkurs**: Jeder Trade wird mit ECB-Kurs vom Handelstag konvertiert

- **Progressive Steuer**: Stufenweise Berechnung nach österr. Einkommensteuergesetz## Requirements 📋



### Fehlerbehandlung:- Python 3.7+

- `requests` library for API calls

- ✅ Pagination für >2000 Trades (automatisch)- `pandas` library for data processing

- ✅ Retry-Logik bei API-Timeouts

- ✅ Währungs-Parsing: Komma UND Punkt als Dezimalzeichen## Error Handling 🔧

- ✅ Datenvalidierung mit aussagekräftigen Fehlermeldungen

The script includes robust error handling for:

---

- Network timeouts and connection issues

## 🎯 Beispiel: Vollständiger Ablauf- API rate limiting

- Invalid responses

### 1️⃣ Programm starten- Missing data fields



```bash## Data Limitations ⚠️

python hyperliquid_fetcher.py

```- Trade history limited to 2000 most recent fills

- Only 10,000 most recent fills available via API

### 2️⃣ Eingaben- For complete historical data, consider using Hyperliquid's S3 archives



```## Example Output 📊

Wallet-Adresse: 0xYourWalletHere

Steuerjahr: 2025```

```🚀 Starting Hyperliquid Data Fetcher...

📊 Wallet Address: 0x2987F53372c02D1a4C67241aA1840C1E83c480fF

### 3️⃣ Einkommen in CSV eintragen════════════════════════════════════════════════════════════════════════════════

📊 Fetching trade history...

Öffne `manual_input/monthly_income.csv`:✅ Retrieved 1717 trade fills

💰 Fetching funding history...

```csv✅ Retrieved 500 funding records

monat,jahr,brutto_gehalt,enabled🔄 Fetching transfer/deposit history...

Januar,2025,3080,1✅ Retrieved 13 transfer records

Februar,2025,3080,1📈 Fetching account state and open positions...

...✅ Retrieved account state

Dezember,2025,3080,1

```╔══════════════════════════════════════════════════════════════════════════════════╗

║                            HYPERLIQUID TRADING SUMMARY                           ║

### 4️⃣ Ergebnis╚══════════════════════════════════════════════════════════════════════════════════╝



```📊 ACCOUNT OVERVIEW

═══════════════════════════════════════════════════════════════💰 Account Value: $10,643.83

🇦🇹 ÖSTERREICHISCHE STEUERKALKULATION 2025💵 Available to Withdraw: $32.14

═══════════════════════════════════════════════════════════════📈 Total Position Value: $25,025.92

💰 Lohn-Einkommen: €36,960.00🔒 Total Margin Used: $10,611.69

📊 Trading-Gewinn (steuerlich): €1,234.56

🔢 Gesamteinkommen (steuerpflichtig): €38,194.56🎯 OPEN POSITIONS (1)

📈 ASTER - LONG

💸 Steuer nur auf Lohn: €6,377.10   Size: 13,014.0000 | Entry: $1.3129

💸 Zusatzsteuer durch Trading: €493.82   Unrealized PnL: $7,940.21 (139.42%)

💰 Steuer gesamt: €6,870.92   Margin Used: $10,611.69 | Max Leverage: 3.0x



────────────────────────────────────────────────────────────────📈 TRADING ACTIVITY (1717 trades)

📋 FÜR STEUERERKLÄRUNG:💰 Total Volume: $3,952,260.63

💰 Trading-Gewinn (E1kv eintragen): €1,234.56💸 Total Fees Paid: $1,622.46

💸 Zusätzlich zu überweisen: €493.82📊 Realized PnL: $440.10

``````



------



## ⚖️ Rechtliche Hinweise**Built for tax reporting and trading analysis** 📋💼


⚠️ **Wichtig**: Dieses Programm ist eine **Berechnungshilfe** und ersetzt keine professionelle Steuerberatung.

- Konsultieren Sie einen **österreichischen Steuerberater** für offizielle Beratung
- Die Berechnungen basieren auf dem **Einkommensteuergesetz 2025**
- Das Programm wurde nach bestem Wissen entwickelt, aber **ohne Gewähr**
- Verwenden Sie die generierten Unterlagen als **Grundlage für Ihre Steuererklärung**

---

## 📞 Support & Entwicklung

**Version**: 3.0 (2025)  
**Sprache**: Python 3.7+  
**Lizenz**: MIT  

### Anforderungen:

```
requests >= 2.31.0
pandas >= 2.0.0
reportlab >= 4.0.0
```

---

## 🎉 Features auf einen Blick

✅ Vollautomatische Datenerfassung von Hyperliquid  
✅ Monatsgenaue Einkommenseingabe via CSV  
✅ Manuelle Ergänzungen für andere Plattformen  
✅ EUR/USD Konvertierung mit offiziellen ECB-Kursen  
✅ Österreichisches Steuerrecht 2025 korrekt implementiert  
✅ PDF-Report für Finanzamt  
✅ ZIP-Export aller Unterlagen  
✅ Komma UND Punkt als Dezimaltrennzeichen  
✅ Enable/Disable System für alle CSV-Einträge  

**Bereit für Ihre österreichische Steuererklärung 2025!** 🇦🇹
