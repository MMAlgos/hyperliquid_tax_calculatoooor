# Hyperliquid Tax Calculator 📊

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

The script is pre-configured with your wallet address: `0x2987F53372c02D1a4C67241aA1840C1E83c480fF`

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
