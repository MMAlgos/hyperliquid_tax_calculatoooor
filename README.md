# 🇦🇹 Austrian Tax Report Generator for Hyperliquid Trading

## ✅ COMPLETE SYSTEM - VERSION 2.0

### 🎯 **Features Implemented**

1. **ECB API Integration** - Real-time EUR/USD conversion with 101 cached exchange rates
2. **Austrian Tax Law 2025** - Complete progressive tax brackets with corrected loss treatment
3. **Separated Tax Display** - Shows Lohn-only vs Trading vs Combined tax calculations
4. **Tax Form Guidance** - Generates detailed PDF instructions for Austrian Steuererklärung
5. **User Input System** - Interactive input for wallet, yearly income, and tax year
6. **Organized Output** - Separate folders for CSV, PDF, and ZIP files
7. **PDF Reports** - Comprehensive Austrian tax reports with proper terminology

### � **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python hyperliquid_fetcher.py
```

### 📋 **What You'll Enter**

- **Wallet Address**: Your Hyperliquid wallet address (0x...)
- **Lohn-Einkommen**: Your yearly salary income in EUR (e.g., 50000)
- **Tax Year**: The year for tax calculation (e.g., 2024)

### 🀽� **Generated Files**

#### CSV Files (Raw Data)

- `trades_WALLET_YEAR.csv` - All trading transactions
- `funding_WALLET_YEAR.csv` - Funding payments/receipts
- `positions_WALLET_YEAR.csv` - Position history

#### PDF Reports

- `Austrian_Tax_Report_WALLET_YEAR.pdf` - Complete tax analysis
- `Ueberweisung_Finanzamt_AT_WALLET_YEAR.pdf` - **Tax form instructions**

#### ZIP Archive

- Complete package with all files for tax submission

### 🇦🇹 **Austrian Tax Form Instructions**

The system generates a **Tax Form Guidance PDF** that shows exactly:

1. **Which forms to use**: E1 (main) + E1kv (capital gains)
2. **Where to enter trading profits**: Specific field references
3. **How much to transfer**: Exact amount for Finanzamt
4. **Step-by-step process**: From FinanzOnline login to submission

### 💡 **Key Austrian Tax Rules Applied**

- ✅ **Losses don't reduce salary income** (corrected implementation)
- ✅ **Only positive trading results are taxable**
- ✅ **Progressive tax brackets 2025** (0% to 55%)
- ✅ **FIFO methodology** for position calculations
- ✅ **Proper German terminology** throughout

### 🔧 **Technical Details**

- **Currency Conversion**: ECB Statistical Data API with daily rates
- **Tax Calculations**: Mathematically verified Austrian progressive system
- **Data Processing**: FIFO-based position tracking
- **PDF Generation**: ReportLab with professional formatting
- **Error Handling**: Robust validation and error reporting

### ⚖️ **Legal Compliance**

This system implements Austrian tax law as of 2025. Always consult with a qualified Austrian tax advisor (Steuerberater) for official tax advice.

---

## 🎯 **EXAMPLE TAX CALCULATION OUTPUT**

```
🇦🇹 ÖSTERREICHISCHE STEUERBERECHNUNG - ERGEBNISSE
════════════════════════════════════════════════════════════════════════════════
💰 Lohn-Einkommen (vom Arbeitgeber): €50,000.00
📊 Trading-Ergebnis (Hyperliquid): €2,532.98
💸 Steuer nur auf Lohn: €7,950.00
📈 Steuer mit Trading: €8,963.19
💡 Zusätzliche Steuer durch Trading: €1,013.19

FÜR STEUERERKLÄRUNG:
📋 Trading-Gewinn (E1kv eintragen): €2,532.98
💳 Zusätzlich zu überweisen: €1,013.19
```

---

**🎉 Ready for Austrian Steuererklärung 2025!**

A comprehensive Python application that fetches all your Hyperliquid trading data including trades, funding history, deposits/withdrawals, and open positions.

## Features ✨

- **Complete Trade History**: Fetches all your trade fills with detailed information
- **Funding History**: Retrieves funding payments/receipts for all positions
- **Transfer History**: Gets deposit and withdrawal records
- **Open Positions**: Shows current positions with unrealized PnL, leverage, and liquidation prices
- **Data Export**: Saves data in CSV, JSON, and text summary formats
- **Clean Summaries**: Generates readable reports with key metrics

## Quick Start 🚀

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Script**:

   ```bash
   python hyperliquid_fetcher.py
   ```

The script is pre-configured with your wallet address: `0x343434238412742847278429874d2`

## What You Get 📈

### Console Output

- Real-time fetching progress
- Complete trading summary with:
  - Account value and available balance
  - Open positions with PnL and leverage
  - Trading statistics (volume, fees, realized PnL)
  - Top traded assets
  - Funding history summary
  - Deposit/withdrawal totals

### Files Generated

- `hyperliquid_trades_[timestamp].csv` - Detailed trade history
- `hyperliquid_funding_[timestamp].csv` - Funding payments/receipts
- `hyperliquid_transfers_[timestamp].csv` - Deposits and withdrawals
- `hyperliquid_summary_[timestamp].txt` - Human-readable summary report
- `hyperliquid_raw_data_[timestamp].json` - Complete raw API responses

## Data Included 📋

### Trade Data

- Timestamp, coin, side (buy/sell), size, price
- Direction (Open Long, Close Short, etc.)
- Closed PnL, fees, starting position
- Transaction hashes and order IDs

### Funding Data

- Funding rates and payments per position
- Position sizes at funding time
- Timestamps and transaction hashes

### Transfer Data

- Deposits, withdrawals, internal transfers
- Amounts and timestamps
- Transaction details

### Account State

- Current account value and margin usage
- Open positions with:
  - Position size and entry price
  - Unrealized PnL and ROE%
  - Margin used and max leverage
  - Liquidation prices

## API Endpoints Used 🔌

- `userFills` - Trade history (max 2000 recent fills)
- `userFunding` - Funding payments/receipts
- `userNonFundingLedgerUpdates` - Deposits/withdrawals
- `clearinghouseState` - Current positions and account info
- `frontendOpenOrders` - Open orders

## Configuration 🛠️

To use with a different wallet address, modify the `wallet_address` variable in the `main()` function:

```python
wallet_address = "0xYourWalletAddressHere"
```

## Requirements 📋

- Python 3.7+
- `requests` library for API calls
- `pandas` library for data processing

## Error Handling 🔧

The script includes robust error handling for:

- Network timeouts and connection issues
- API rate limiting
- Invalid responses
- Missing data fields

## Data Limitations ⚠️

- Trade history limited to 2000 most recent fills
- Only 10,000 most recent fills available via API
- For complete historical data, consider using Hyperliquid's S3 archives

## Example Output 📊

```
🚀 Starting Hyperliquid Data Fetcher...
📊 Wallet Address: 0x2987F53372c02D1a4C67241aA1840C1E83c480fF
════════════════════════════════════════════════════════════════════════════════
📊 Fetching trade history...
✅ Retrieved 1717 trade fills
💰 Fetching funding history...
✅ Retrieved 500 funding records
🔄 Fetching transfer/deposit history...
✅ Retrieved 13 transfer records
📈 Fetching account state and open positions...
✅ Retrieved account state

╔══════════════════════════════════════════════════════════════════════════════════╗
║                            HYPERLIQUID TRADING SUMMARY                           ║
╚══════════════════════════════════════════════════════════════════════════════════╝

📊 ACCOUNT OVERVIEW
💰 Account Value: $10,643.83
💵 Available to Withdraw: $32.14
📈 Total Position Value: $25,025.92
🔒 Total Margin Used: $10,611.69

🎯 OPEN POSITIONS (1)
📈 ASTER - LONG
   Size: 13,014.0000 | Entry: $1.3129
   Unrealized PnL: $7,940.21 (139.42%)
   Margin Used: $10,611.69 | Max Leverage: 3.0x

📈 TRADING ACTIVITY (1717 trades)
💰 Total Volume: $3,952,260.63
💸 Total Fees Paid: $1,622.46
📊 Realized PnL: $440.10
```

---

**Built for tax reporting and trading analysis** 📋💼
