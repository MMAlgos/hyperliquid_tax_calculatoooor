"""
Hyperliquid Tax Calculator
Fetches all trading data from Hyperliquid including trades, funding, transfers, and open positions
"""

import requests
import json
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time

class HyperliquidFetcher:
    """Class to fetch and process Hyperliquid trading data"""
    
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address.lower()
        self.api_url = "https://api.hyperliquid.xyz/info"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HyperliquidTaxCalculator/1.0'
        })
    
    def _make_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a POST request to the Hyperliquid API with error handling"""
        try:
            response = self.session.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def get_user_fills(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch user fills (trade history)
        Returns at most 2000 fills per request, only 10000 most recent available
        """
        print("📊 Fetching trade history...")
        
        if start_time or end_time:
            payload = {
                "type": "userFillsByTime",
                "user": self.wallet_address,
                "startTime": start_time or 0,
                "endTime": end_time or int(time.time() * 1000),
                "aggregateByTime": False
            }
        else:
            payload = {
                "type": "userFills",
                "user": self.wallet_address,
                "aggregateByTime": False
            }
        
        result = self._make_request(payload)
        if result:
            print(f"✅ Retrieved {len(result)} trade fills")
            return result
        return []
    
    def get_user_funding(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch user funding history"""
        print("💰 Fetching funding history...")
        
        payload = {
            "type": "userFunding",
            "user": self.wallet_address,
            "startTime": start_time or 0,
            "endTime": end_time or int(time.time() * 1000)
        }
        
        result = self._make_request(payload)
        if result:
            print(f"✅ Retrieved {len(result)} funding records")
            return result
        return []
    
    def get_user_transfers(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch user non-funding ledger updates (deposits, withdrawals, transfers)"""
        print("🔄 Fetching transfer/deposit history...")
        
        payload = {
            "type": "userNonFundingLedgerUpdates",
            "user": self.wallet_address,
            "startTime": start_time or 0,
            "endTime": end_time or int(time.time() * 1000)
        }
        
        result = self._make_request(payload)
        if result:
            print(f"✅ Retrieved {len(result)} transfer records")
            return result
        return []
    
    def get_account_state(self) -> Optional[Dict[str, Any]]:
        """Fetch current account state including open positions"""
        print("📈 Fetching account state and open positions...")
        
        payload = {
            "type": "clearinghouseState",
            "user": self.wallet_address
        }
        
        result = self._make_request(payload)
        if result:
            print("✅ Retrieved account state")
            return result
        return None
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Fetch current open orders"""
        print("📋 Fetching open orders...")
        
        payload = {
            "type": "frontendOpenOrders",
            "user": self.wallet_address
        }
        
        result = self._make_request(payload)
        if result:
            print(f"✅ Retrieved {len(result)} open orders")
            return result
        return []

class HyperliquidDataProcessor:
    """Class to process and summarize Hyperliquid data"""
    
    @staticmethod
    def timestamp_to_datetime(timestamp_ms: int) -> str:
        """Convert timestamp in milliseconds to readable datetime"""
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    @staticmethod
    def process_trades(trades: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process trade fills into a clean DataFrame"""
        if not trades:
            return pd.DataFrame()
        
        processed_trades = []
        
        for trade in trades:
            processed_trade = {
                'timestamp': HyperliquidDataProcessor.timestamp_to_datetime(trade['time']),
                'coin': trade['coin'],
                'side': 'Buy' if trade['side'] == 'B' else 'Sell',
                'size': float(trade['sz']),
                'price': float(trade['px']),
                'direction': trade.get('dir', 'N/A'),
                'closed_pnl': float(trade.get('closedPnl', 0)),
                'fee': float(trade.get('fee', 0)),
                'fee_token': trade.get('feeToken', 'USDC'),
                'start_position': float(trade.get('startPosition', 0)),
                'hash': trade['hash'],
                'order_id': trade['oid'],
                'crossed': trade.get('crossed', False),
                'trade_id': trade.get('tid', ''),
                'builder_fee': float(trade.get('builderFee', 0))
            }
            processed_trades.append(processed_trade)
        
        df = pd.DataFrame(processed_trades)
        df = df.sort_values('timestamp', ascending=False)
        return df
    
    @staticmethod
    def process_funding(funding: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process funding history into a clean DataFrame"""
        if not funding:
            return pd.DataFrame()
        
        processed_funding = []
        
        for fund in funding:
            delta = fund['delta']
            processed_fund = {
                'timestamp': HyperliquidDataProcessor.timestamp_to_datetime(fund['time']),
                'coin': delta['coin'],
                'funding_rate': float(delta.get('fundingRate', 0)),
                'position_size': float(delta.get('szi', 0)),
                'funding_payment': float(delta.get('usdc', 0)),
                'type': delta.get('type', 'funding'),
                'hash': fund['hash']
            }
            processed_funding.append(processed_fund)
        
        df = pd.DataFrame(processed_funding)
        df = df.sort_values('timestamp', ascending=False)
        return df
    
    @staticmethod
    def process_transfers(transfers: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process transfer/deposit history into a clean DataFrame"""
        if not transfers:
            return pd.DataFrame()
        
        processed_transfers = []
        
        for transfer in transfers:
            delta = transfer['delta']
            processed_transfer = {
                'timestamp': HyperliquidDataProcessor.timestamp_to_datetime(transfer['time']),
                'type': delta.get('type', 'unknown'),
                'amount': float(delta.get('usdc', 0)) if 'usdc' in delta else 0,
                'coin': delta.get('coin', 'USDC'),
                'hash': transfer['hash']
            }
            
            # Handle different transfer types
            if 'subAccountTransfer' in delta:
                processed_transfer['details'] = f"SubAccount Transfer: {delta['subAccountTransfer']}"
            elif 'spotTransfer' in delta:
                processed_transfer['details'] = f"Spot Transfer: {delta['spotTransfer']}"
            else:
                processed_transfer['details'] = str(delta)
            
            processed_transfers.append(processed_transfer)
        
        df = pd.DataFrame(processed_transfers)
        df = df.sort_values('timestamp', ascending=False)
        return df
    
    @staticmethod
    def process_account_state(account_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process account state and open positions"""
        if not account_state:
            return {}
        
        processed_state = {
            'timestamp': HyperliquidDataProcessor.timestamp_to_datetime(account_state.get('time', 0)),
            'account_value': float(account_state['marginSummary']['accountValue']),
            'total_margin_used': float(account_state['marginSummary']['totalMarginUsed']),
            'total_ntl_pos': float(account_state['marginSummary']['totalNtlPos']),
            'total_raw_usd': float(account_state['marginSummary']['totalRawUsd']),
            'withdrawable': float(account_state.get('withdrawable', 0)),
            'cross_maintenance_margin': float(account_state.get('crossMaintenanceMarginUsed', 0)),
            'positions': []
        }
        
        # Process open positions
        for position in account_state.get('assetPositions', []):
            if position['position']['szi'] != '0.0':  # Only non-zero positions
                pos_data = {
                    'coin': position['position']['coin'],
                    'size': float(position['position']['szi']),
                    'entry_px': float(position['position'].get('entryPx', 0)),
                    'unrealized_pnl': float(position['position'].get('unrealizedPnl', 0)),
                    'return_on_equity': position['position'].get('returnOnEquity', '0%'),
                    'position_value': float(position['position'].get('positionValue', 0)),
                    'margin_used': float(position['position'].get('marginUsed', 0)),
                    'max_leverage': float(position['position'].get('maxLeverage', 0)),
                    'liquidation_px': position['position'].get('liquidationPx', 'N/A')
                }
                processed_state['positions'].append(pos_data)
        
        return processed_state

def create_summary_report(wallet_address: str, trades_df: pd.DataFrame, funding_df: pd.DataFrame, 
                         transfers_df: pd.DataFrame, account_state: Dict[str, Any]) -> str:
    """Create a comprehensive summary report"""
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                            HYPERLIQUID TRADING SUMMARY                           ║
║                            Wallet: {wallet_address}                            ║
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
    
    # Trading summary
    if not trades_df.empty:
        total_volume = (trades_df['size'] * trades_df['price']).sum()
        total_fees = trades_df['fee'].sum()
        total_pnl = trades_df['closed_pnl'].sum()
        unique_coins = trades_df['coin'].nunique()
        buy_trades = len(trades_df[trades_df['side'] == 'Buy'])
        sell_trades = len(trades_df[trades_df['side'] == 'Sell'])
        
        report += f"""

📈 TRADING ACTIVITY ({len(trades_df)} trades)
─────────────────────────────────────────────────────────────────────────────────
💎 Unique Assets Traded: {unique_coins}
🟢 Buy Trades: {buy_trades} | 🔴 Sell Trades: {sell_trades}
💰 Total Volume: ${total_volume:,.2f}
💸 Total Trading Fees: ${abs(total_fees):,.4f}
📊 Realized PnL: ${total_pnl:,.2f}

🏆 TOP TRADED ASSETS:"""
        
        top_coins = trades_df.groupby('coin').agg({
            'size': 'count',
            'price': lambda x: (trades_df.loc[x.index, 'size'] * x).sum()
        }).rename(columns={'size': 'trades', 'price': 'volume'}).sort_values('volume', ascending=False).head(5)
        
        for coin, data in top_coins.iterrows():
            report += f"""
   {coin}: {data['trades']} trades, ${data['volume']:,.2f} volume"""
    else:
        report += "\n\n📈 TRADING ACTIVITY\n─────────────────────────────────────────────────────────────────────────────────\n   No trades found"
    
    # Funding summary
    if not funding_df.empty:
        total_funding = funding_df['funding_payment'].sum()
        funding_coins = funding_df['coin'].nunique()
        
        report += f"""

💰 FUNDING HISTORY ({len(funding_df)} payments)
─────────────────────────────────────────────────────────────────────────────────
💸 Total Funding Paid/Received: ${total_funding:,.4f}
📊 Assets with Funding: {funding_coins}"""
        
        funding_by_coin = funding_df.groupby('coin')['funding_payment'].sum().sort_values().head(5)
        for coin, amount in funding_by_coin.items():
            status = "Paid" if amount < 0 else "Received"
            report += f"""
   {coin}: ${abs(amount):,.4f} {status}"""
    else:
        total_funding = 0
        report += "\n\n💰 FUNDING HISTORY\n─────────────────────────────────────────────────────────────────────────────────\n   No funding records found"
    
    # Combined costs summary
    total_fees = trades_df['fee'].sum() if not trades_df.empty else 0
    total_costs = abs(total_fees) + abs(total_funding)
    
    report += f"""

💳 TOTAL COSTS BREAKDOWN
─────────────────────────────────────────────────────────────────────────────────
💸 Trading Fees: ${abs(total_fees):,.4f}
🔄 Funding Costs: ${abs(total_funding):,.4f}
💰 Combined Total: ${total_costs:,.4f}"""
    
    # Transfer summary
    if not transfers_df.empty:
        deposits = transfers_df[transfers_df['type'].str.contains('deposit|withdraw', case=False, na=False)]
        total_deposits = deposits[deposits['amount'] > 0]['amount'].sum()
        total_withdrawals = abs(deposits[deposits['amount'] < 0]['amount'].sum())
        
        report += f"""

🔄 DEPOSITS & WITHDRAWALS ({len(transfers_df)} records)
─────────────────────────────────────────────────────────────────────────────────
📥 Total Deposits: ${total_deposits:,.2f}
📤 Total Withdrawals: ${total_withdrawals:,.2f}
💰 Net Flow: ${total_deposits - total_withdrawals:,.2f}"""
    else:
        report += "\n\n🔄 DEPOSITS & WITHDRAWALS\n─────────────────────────────────────────────────────────────────────────────────\n   No transfer records found"
    
    report += f"""

📅 REPORT GENERATED: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    
    return report

def main():
    """Main function to run the Hyperliquid data fetcher"""
    wallet_address = "0x2987F53372c02D1a4C67241aA1840C1E83c480fF"
    
    print("🚀 Starting Hyperliquid Data Fetcher...")
    print(f"📊 Wallet Address: {wallet_address}")
    print("═" * 80)
    
    # Initialize fetcher
    fetcher = HyperliquidFetcher(wallet_address)
    processor = HyperliquidDataProcessor()
    
    # Fetch all data
    try:
        # Get trades
        trades_data = fetcher.get_user_fills()
        trades_df = processor.process_trades(trades_data)
        
        # Get funding
        funding_data = fetcher.get_user_funding()
        funding_df = processor.process_funding(funding_data)
        
        # Get transfers
        transfers_data = fetcher.get_user_transfers()
        transfers_df = processor.process_transfers(transfers_data)
        
        # Get account state
        account_data = fetcher.get_account_state()
        account_state = processor.process_account_state(account_data) if account_data else {}
        
        # Get open orders
        open_orders = fetcher.get_open_orders()
        
        print("\n" + "═" * 80)
        print("📊 DATA FETCHING COMPLETE!")
        print("═" * 80)
        
        # Create and display summary
        summary = create_summary_report(wallet_address, trades_df, funding_df, transfers_df, account_state)
        print(summary)
        
        # Save data to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not trades_df.empty:
            trades_df.to_csv(f'hyperliquid_trades_{timestamp}.csv', index=False)
            print(f"💾 Trades saved to: hyperliquid_trades_{timestamp}.csv")
        
        if not funding_df.empty:
            funding_df.to_csv(f'hyperliquid_funding_{timestamp}.csv', index=False)
            print(f"💾 Funding saved to: hyperliquid_funding_{timestamp}.csv")
        
        if not transfers_df.empty:
            transfers_df.to_csv(f'hyperliquid_transfers_{timestamp}.csv', index=False)
            print(f"💾 Transfers saved to: hyperliquid_transfers_{timestamp}.csv")
        
        # Save summary report
        with open(f'hyperliquid_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"📄 Summary saved to: hyperliquid_summary_{timestamp}.txt")
        
        # Save raw JSON data
        all_data = {
            'wallet_address': wallet_address,
            'timestamp': timestamp,
            'trades': trades_data,
            'funding': funding_data,
            'transfers': transfers_data,
            'account_state': account_data,
            'open_orders': open_orders
        }
        
        with open(f'hyperliquid_raw_data_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, default=str)
        print(f"🗂️  Raw data saved to: hyperliquid_raw_data_{timestamp}.json")
        
        print("\n✅ All data successfully fetched and saved!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
