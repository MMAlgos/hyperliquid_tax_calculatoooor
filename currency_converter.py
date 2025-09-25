"""
EUR Currency Converter for Hyperliquid Tax Calculator
Fetches ECB exchange rates and converts USD amounts to EUR
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import io
from typing import Dict, Optional

class ECBRatesFetcher:
    """Fetches EUR/USD exchange rates from European Central Bank Statistical Data API"""
    
    def __init__(self):
        self.base_url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
        self.session = requests.Session()
        self.rates_cache = {}
        self.rates_file = "ecb_rates_cache.json"
        
    def load_cached_rates(self) -> Dict[str, float]:
        """Load previously cached rates from file"""
        try:
            with open(self.rates_file, 'r') as f:
                self.rates_cache = json.load(f)
                print(f"📊 Loaded {len(self.rates_cache)} cached exchange rates")
        except FileNotFoundError:
            print("📊 No cached rates found, will fetch from ECB")
            self.rates_cache = {}
        return self.rates_cache
    
    def save_cached_rates(self):
        """Save rates to cache file"""
        with open(self.rates_file, 'w') as f:
            json.dump(self.rates_cache, f, indent=2)
        print(f"💾 Saved {len(self.rates_cache)} exchange rates to cache")
    
    def fetch_ecb_rates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, float]:
        """Fetch historical EUR/USD rates from ECB Statistical Data API"""
        print("🌍 Fetching EUR/USD rates from European Central Bank Statistical Data API...")
        
        try:
            # Build parameters for the API call
            params = {"format": "csvdata"}
            
            if start_date and end_date:
                params["startPeriod"] = start_date
                params["endPeriod"] = end_date
                print(f"📅 Requesting rates from {start_date} to {end_date}")
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse CSV response using pandas
            df = pd.read_csv(io.StringIO(response.text))
            
            rates = {}
            
            # Process the CSV data
            for _, row in df.iterrows():
                if 'TIME_PERIOD' in row and 'OBS_VALUE' in row and pd.notna(row['OBS_VALUE']):
                    date_str = row['TIME_PERIOD']
                    # ECB gives USD per 1 EUR (e.g., 1.10), we want EUR per 1 USD so we need 1/rate
                    usd_per_eur = float(row['OBS_VALUE'])
                    eur_per_usd = 1.0 / usd_per_eur
                    rates[date_str] = eur_per_usd
            
            print(f"✅ Fetched {len(rates)} EUR/USD exchange rates from ECB Statistical Data API")
            self.rates_cache.update(rates)
            self.save_cached_rates()
            return rates
            
        except Exception as e:
            print(f"❌ Failed to fetch ECB rates from Statistical Data API: {e}")
            print("🔄 Falling back to cache or default rates...")
            return {}
    
    def get_rate_for_date(self, date_str: str) -> Optional[float]:
        """Get EUR/USD rate for a specific date (YYYY-MM-DD format)"""
        # Try exact date first
        if date_str in self.rates_cache:
            return self.rates_cache[date_str]
        
        # Try previous dates (ECB doesn't publish rates on weekends/holidays)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        for i in range(1, 15):  # Try up to 15 days back
            check_date = date_obj - timedelta(days=i)
            check_date_str = check_date.strftime('%Y-%m-%d')
            
            if check_date_str in self.rates_cache:
                return self.rates_cache[check_date_str]
        
        # If we don't have the rate, return None to trigger a fetch
        return None
    
    def ensure_rates_available(self, dates_needed: list):
        """Ensure we have rates for all required dates"""
        # Load cached rates first
        self.load_cached_rates()
        
        if not dates_needed:
            return
        
        # Find date range we need
        dates_needed_set = set(dates_needed)
        missing_dates = []
        
        for date_str in dates_needed_set:
            if self.get_rate_for_date(date_str) is None:  # Changed to check for None specifically
                missing_dates.append(date_str)
        
        if missing_dates:
            # Determine date range to fetch
            min_date = min(missing_dates)
            max_date = max(missing_dates)
            
            # Extend range by a few days to ensure we get weekend/holiday coverage
            min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
            max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')
            
            start_date = (min_date_obj - timedelta(days=10)).strftime('%Y-%m-%d')
            end_date = (max_date_obj + timedelta(days=5)).strftime('%Y-%m-%d')
            
            # Don't fetch future dates beyond today
            today = datetime.now().strftime('%Y-%m-%d')
            if end_date > today:
                end_date = today
            
            print(f"📊 Need rates for {len(missing_dates)} dates, fetching range {start_date} to {end_date}...")
            self.fetch_ecb_rates(start_date, end_date)

class CurrencyConverter:
    """Converts USD amounts to EUR using ECB rates"""
    
    def __init__(self):
        self.rates_fetcher = ECBRatesFetcher()
    
    def prepare_rates(self, df_list: list):
        """Prepare exchange rates for all dataframes"""
        all_dates = set()
        
        for df in df_list:
            if not df.empty and 'timestamp' in df.columns:
                # Extract dates from timestamps
                dates = pd.to_datetime(df['timestamp']).dt.date.astype(str).unique()
                all_dates.update(dates)
        
        # Ensure we have rates for all dates
        if all_dates:
            self.rates_fetcher.ensure_rates_available(list(all_dates))
    
    def add_eur_conversions(self, df: pd.DataFrame, amount_columns: list) -> pd.DataFrame:
        """Add EUR conversion columns to a dataframe"""
        if df.empty:
            return df
        
        df_copy = df.copy()
        
        # Add exchange rate column
        df_copy['date'] = pd.to_datetime(df_copy['timestamp']).dt.date.astype(str)
        
        def get_rate_with_fallback(date_str):
            """Get rate with fallback logic"""
            rate = self.rates_fetcher.get_rate_for_date(date_str)
            if rate is not None:
                return rate
            
            # Fallback: use a recent rate if available
            if self.rates_fetcher.rates_cache:
                latest_date = max(self.rates_fetcher.rates_cache.keys())
                latest_rate = self.rates_fetcher.rates_cache[latest_date]
                print(f"📅 Using latest available rate {latest_rate} from {latest_date} for {date_str}")
                return latest_rate
            
            # Ultimate fallback
            print(f"⚠️  Using fallback EUR/USD rate 0.90 for {date_str}")
            return 0.90
        
        df_copy['usd_eur_rate'] = df_copy['date'].apply(get_rate_with_fallback)
        
        # Convert USD amounts to EUR
        for col in amount_columns:
            if col in df_copy.columns:
                eur_col = col + '_eur'  # Always add _eur suffix
                # Handle None values and ensure numeric conversion
                df_copy[eur_col] = pd.to_numeric(df_copy[col], errors='coerce') * pd.to_numeric(df_copy['usd_eur_rate'], errors='coerce')
                df_copy[eur_col] = df_copy[eur_col].round(4)
        
        return df_copy

def create_enhanced_summary_report(wallet_address: str, trades_df: pd.DataFrame, funding_df: pd.DataFrame, 
                                 transfers_df: pd.DataFrame, account_state: Dict) -> str:
    """Create a comprehensive summary report with USD and EUR amounts"""
    
    # Calculate totals in both currencies
    total_fees_usd = abs(trades_df['fee'].sum()) if not trades_df.empty else 0
    total_fees_eur = abs(trades_df['fee_eur'].sum()) if not trades_df.empty and 'fee_eur' in trades_df.columns else 0
    
    # Separate funding paid and received
    funding_paid_usd = abs(funding_df[funding_df['funding_payment'] < 0]['funding_payment'].sum()) if not funding_df.empty else 0
    funding_received_usd = abs(funding_df[funding_df['funding_payment'] > 0]['funding_payment'].sum()) if not funding_df.empty else 0
    funding_paid_eur = abs(funding_df[funding_df['funding_payment_eur'] < 0]['funding_payment_eur'].sum()) if not funding_df.empty and 'funding_payment_eur' in funding_df.columns else 0
    funding_received_eur = abs(funding_df[funding_df['funding_payment_eur'] > 0]['funding_payment_eur'].sum()) if not funding_df.empty and 'funding_payment_eur' in funding_df.columns else 0
    
    total_pnl_usd = trades_df['closed_pnl'].sum() if not trades_df.empty else 0
    total_pnl_eur = trades_df['closed_pnl_eur'].sum() if not trades_df.empty and 'closed_pnl_eur' in trades_df.columns else 0
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                       HYPERLIQUID TAX REPORT (USD/EUR)                          ║
║                       Wallet: {wallet_address}                       ║
╚══════════════════════════════════════════════════════════════════════════════════╝

📊 ACCOUNT OVERVIEW
─────────────────────────────────────────────────────────────────────────────────
💰 Account Value: ${account_state.get('account_value', 0):,.2f}
💵 Available to Withdraw: ${account_state.get('withdrawable', 0):,.2f}
📈 Total Position Value: ${account_state.get('total_ntl_pos', 0):,.2f}
🔒 Total Margin Used: ${account_state.get('total_margin_used', 0):,.2f}
📅 Last Updated: {account_state.get('timestamp', 'N/A')}

🎯 OPEN POSITIONS ({len(account_state.get('positions', []))})
─────────────────────────────────────────────────────────────────────────────────"""
    
    # Open positions details
    if account_state.get('positions'):
        for pos in account_state['positions']:
            direction = "LONG" if pos['size'] > 0 else "SHORT"
            report += f"""
📈 {pos['coin']} - {direction}
   Size: {pos['size']:,.4f} | Entry: ${pos['entry_px']:,.4f}
   Unrealized PnL: ${pos['unrealized_pnl']:,.2f} ({pos['return_on_equity']})
   Margin Used: ${pos['margin_used']:,.2f} | Max Leverage: {pos['max_leverage']:.1f}x
   Liquidation Price: {pos['liquidation_px']}"""
    else:
        report += "\n   No open positions"
    
    # Trading summary with dual currency
    if not trades_df.empty:
        total_volume_usd = (trades_df['size'] * trades_df['price']).sum()
        unique_coins = trades_df['coin'].nunique()
        buy_trades = len(trades_df[trades_df['side'] == 'Buy'])
        sell_trades = len(trades_df[trades_df['side'] == 'Sell'])
        
        report += f"""

📈 TRADING ACTIVITY ({len(trades_df)} trades)
─────────────────────────────────────────────────────────────────────────────────
💎 Unique Assets Traded: {unique_coins}
🟢 Buy Trades: {buy_trades} | 🔴 Sell Trades: {sell_trades}
💰 Total Volume: ${total_volume_usd:,.2f}
💸 Total Trading Fees: ${total_fees_usd:,.4f} | €{total_fees_eur:,.4f}
📊 Realized PnL: ${total_pnl_usd:,.4f} | €{total_pnl_eur:,.4f}"""
    else:
        report += "\n\n📈 TRADING ACTIVITY\n─────────────────────────────────────────────────────────────────────────────────\n   No trades found"
    
    # Funding summary with dual currency
    if not funding_df.empty:
        funding_coins = funding_df['coin'].nunique()
        
        report += f"""

💰 FUNDING HISTORY ({len(funding_df)} payments)
─────────────────────────────────────────────────────────────────────────────────
💸 Total Funding Paid: ${funding_paid_usd:,.4f} | €{funding_paid_eur:,.4f}
💰 Total Funding Received: ${funding_received_usd:,.4f} | €{funding_received_eur:,.4f}
📊 Assets with Funding: {funding_coins}"""
    else:
        report += "\n\n💰 FUNDING HISTORY\n─────────────────────────────────────────────────────────────────────────────────\n   No funding records found"
    
    # Combined costs summary with dual currency
    total_deductible_costs_usd = total_fees_usd + funding_paid_usd
    total_deductible_costs_eur = total_fees_eur + funding_paid_eur
    net_trading_costs_usd = total_deductible_costs_usd - funding_received_usd
    net_trading_costs_eur = total_deductible_costs_eur - funding_received_eur
    
    report += f"""

💳 TOTAL COSTS BREAKDOWN (Tax Deductible)
─────────────────────────────────────────────────────────────────────────────────
💸 Trading Fees: ${total_fees_usd:,.4f} | €{total_fees_eur:,.4f}
🔄 Funding Paid (abzugsfähig): ${funding_paid_usd:,.4f} | €{funding_paid_eur:,.4f}
💰 Funding Received (Ertrag): ${funding_received_usd:,.4f} | €{funding_received_eur:,.4f}

� SUMME - Abzugsfähige Kosten: ${total_deductible_costs_usd:,.4f} | €{total_deductible_costs_eur:,.4f}
📈 NETTO - Trading-Kosten (Kosten - Erträge): ${net_trading_costs_usd:,.4f} | €{net_trading_costs_eur:,.4f}"""
    
    # Transfer summary
    if not transfers_df.empty:
        deposits = transfers_df[transfers_df['type'].str.contains('deposit|withdraw', case=False, na=False)]
        total_deposits_usd = deposits[deposits['amount'] > 0]['amount'].sum()
        total_withdrawals_usd = abs(deposits[deposits['amount'] < 0]['amount'].sum())
        
        # EUR conversions for deposits/withdrawals if available
        if 'amount_eur' in transfers_df.columns:
            total_deposits_eur = deposits[deposits['amount'] > 0]['amount_eur'].sum()
            total_withdrawals_eur = abs(deposits[deposits['amount'] < 0]['amount_eur'].sum())
            
            report += f"""

🔄 DEPOSITS & WITHDRAWALS ({len(transfers_df)} records)
─────────────────────────────────────────────────────────────────────────────────
📥 Total Deposits: ${total_deposits_usd:,.2f} | €{total_deposits_eur:,.2f}
📤 Total Withdrawals: ${total_withdrawals_usd:,.2f} | €{total_withdrawals_eur:,.2f}
💰 Net Flow: ${total_deposits_usd - total_withdrawals_usd:,.2f} | €{total_deposits_eur - total_withdrawals_eur:,.2f}"""
        else:
            report += f"""

🔄 DEPOSITS & WITHDRAWALS ({len(transfers_df)} records)
─────────────────────────────────────────────────────────────────────────────────
📥 Total Deposits: ${total_deposits_usd:,.2f}
📤 Total Withdrawals: ${total_withdrawals_usd:,.2f}
💰 Net Flow: ${total_deposits_usd - total_withdrawals_usd:,.2f}"""
    else:
        report += "\n\n🔄 DEPOSITS & WITHDRAWALS\n─────────────────────────────────────────────────────────────────────────────────\n   No transfer records found"
    
    report += f"""

📄 TAX REPORTING NOTES
─────────────────────────────────────────────────────────────────────────────────
🇪🇺 EUR conversions use ECB daily reference rates
📅 Closed trades use exchange rate from closing date
🇦🇹 In AT sind **Trading Fees** und **Funding Paid** abzugsfähig; **Funding Received** ist steuerpflichtiger Ertrag
🏦 Deposits sind nicht steuerpflichtig; Withdrawals sind kein Einkommen
📊 Nur **realisierte** PnL ist steuerpflichtig (unrealisierte PnL = Info)
💼 No holding period requirements - all gains taxable as income

📅 REPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    
    return report
