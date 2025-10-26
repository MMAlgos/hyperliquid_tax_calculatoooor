"""
Manual Input Handler - CSV-based system for manual deposits and trades
User edits CSV files with their data, system processes them automatically
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Tuple
from currency_converter import ECBRatesFetcher


class ManualInputHandler:
    """Handles manual input via CSV files"""
    
    def __init__(self, manual_input_folder: str = "manual_input"):
        self.manual_input_folder = manual_input_folder
        self.deposits_csv = os.path.join(manual_input_folder, "manual_deposits.csv")
        self.trades_csv = os.path.join(manual_input_folder, "manual_trades.csv")
        self.income_csv = os.path.join(manual_input_folder, "monthly_income.csv")
        self.converter = ECBRatesFetcher()
        
    def create_manual_input_folder(self):
        """Create manual_input folder if it doesn't exist"""
        if not os.path.exists(self.manual_input_folder):
            os.makedirs(self.manual_input_folder)
            print(f"✅ Ordner erstellt: {self.manual_input_folder}/")
        
    def generate_template_csvs(self):
        """Generate template CSV files with empty data for user to fill in"""
        self.create_manual_input_folder()
        
        # Generate deposits template (empty, ready for user data)
        if not os.path.exists(self.deposits_csv):
            deposits_template = pd.DataFrame({
                'date': ['2025-01-01'],
                'amount': [0.00],
                'currency': ['EUR'],
                'type': ['deposit'],
                'description': ['Beispiel - Ersetzen oder löschen'],
                'enabled': [0]  # 0=disabled by default
            })
            deposits_template.to_csv(self.deposits_csv, index=False, encoding='utf-8')
            print(f"✅ Template erstellt: {self.deposits_csv}")
            print(f"   📝 Fügen Sie Ihre Einzahlungen von anderen Plattformen hinzu!")
        
        # Generate trades template (empty, ready for user data)
        if not os.path.exists(self.trades_csv):
            trades_template = pd.DataFrame({
                'date': ['2025-01-01'],
                'coin': ['EXAMPLE'],
                'side': ['buy'],
                'size': [0.00],
                'price': [0.00],
                'currency': ['USD'],
                'leverage': [1],
                'fee': [0.00],
                'pnl': [0.00],
                'description': ['Beispiel - Ersetzen oder löschen'],
                'enabled': [0]  # 0=disabled by default
            })
            trades_template.to_csv(self.trades_csv, index=False, encoding='utf-8')
            print(f"✅ Template erstellt: {self.trades_csv}")
            print(f"   📝 Fügen Sie Ihre Trades von anderen Plattformen hinzu!")
        
        # Generate monthly income template
        if not os.path.exists(self.income_csv):
            # Create template for current year with all 12 months
            current_year = datetime.now().year
            months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                     'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
            
            income_template = pd.DataFrame({
                'monat': months,
                'jahr': [current_year] * 12,
                'brutto_gehalt': [0.00] * 12,
                'enabled': [1] * 12
            })
            income_template.to_csv(self.income_csv, index=False, encoding='utf-8')
            print(f"✅ Template erstellt: {self.income_csv}")
            print(f"   📝 Tragen Sie Ihr monatliches Brutto-Gehalt ein!")
    
    def read_monthly_income(self, tax_year: int = None) -> float:
        """Read monthly income from CSV and calculate total yearly income
        
        Args:
            tax_year: Optional year to filter income entries. If None, uses all enabled entries.
        """
        if not os.path.exists(self.income_csv):
            print(f"ℹ️  Keine monatlichen Einkommen gefunden: {self.income_csv}")
            return None
        
        try:
            df = pd.read_csv(self.income_csv, encoding='utf-8')
            
            # Convert brutto_gehalt to float, handling both comma and dot as decimal separator
            def parse_amount(value):
                """Parse amount supporting both comma (5643,64) and dot (5643.64) as decimal separator"""
                if pd.isna(value):
                    return 0.0
                if isinstance(value, (int, float)):
                    return float(value)
                # Convert string: replace comma with dot, remove quotes
                value_str = str(value).strip().strip('"').strip("'")
                value_str = value_str.replace(',', '.')
                try:
                    return float(value_str)
                except ValueError:
                    print(f"⚠️  Warnung: Ungültiger Betrag '{value}' wird als 0.0 behandelt")
                    return 0.0
            
            df['brutto_gehalt'] = df['brutto_gehalt'].apply(parse_amount)
            
            # Filter by tax year if provided
            if tax_year is not None and 'jahr' in df.columns:
                df = df[df['jahr'] == tax_year]
                if df.empty:
                    print(f"ℹ️  Keine Einkommen für Jahr {tax_year} in {self.income_csv}")
                    return None
            
            # Filter only enabled entries
            if 'enabled' in df.columns:
                df = df[df['enabled'] == 1]
            
            if df.empty:
                print(f"ℹ️  Keine aktiven Einkommen in {self.income_csv}")
                return None
            
            # Calculate total yearly income
            total_income = df['brutto_gehalt'].sum()
            
            print(f"📊 Monatliches Einkommen geladen:")
            for _, row in df.iterrows():
                if row['brutto_gehalt'] > 0:
                    print(f"   {row['monat']} {int(row['jahr'])}: €{row['brutto_gehalt']:,.2f}")
            
            print(f"✅ Jahresgesamteinkommen: €{total_income:,.2f}")
            return total_income
            
        except Exception as e:
            print(f"❌ Fehler beim Lesen der monatlichen Einkommen: {e}")
            return None
    
    def read_manual_deposits(self) -> pd.DataFrame:
        """Read and process manual deposits from CSV"""
        if not os.path.exists(self.deposits_csv):
            print(f"ℹ️  Keine manuellen Einzahlungen gefunden: {self.deposits_csv}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(self.deposits_csv, encoding='utf-8')
            
            # Filter only enabled entries
            if 'enabled' in df.columns:
                df = df[df['enabled'] == 1]
            
            if df.empty:
                print(f"ℹ️  Keine aktiven Einzahlungen in {self.deposits_csv}")
                return pd.DataFrame()
            
            print(f"📥 Verarbeite {len(df)} manuelle Einzahlung(en)...")
            
            # Ensure we have exchange rates for all dates
            dates_needed = df['date'].tolist()
            self.converter.ensure_rates_available(dates_needed)
            
            # Process each deposit
            processed_deposits = []
            for idx, row in df.iterrows():
                deposit = self._process_deposit_row(row)
                if deposit:
                    processed_deposits.append(deposit)
            
            if processed_deposits:
                result_df = pd.DataFrame(processed_deposits)
                print(f"✅ {len(processed_deposits)} Einzahlung(en) erfolgreich verarbeitet")
                return result_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Fehler beim Lesen von {self.deposits_csv}: {e}")
            return pd.DataFrame()
    
    def _process_deposit_row(self, row: pd.Series) -> Dict:
        """Process a single deposit row with EUR/USD conversion"""
        try:
            # Parse date
            date_str = str(row['date'])
            deposit_date = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = int(deposit_date.timestamp() * 1000)
            
            # Get amount and currency
            amount = float(row['amount'])
            currency = str(row['currency']).upper()
            trans_type = str(row['type']).lower()
            description = str(row.get('description', f'Manual {trans_type}'))
            
            # Get exchange rate for that date
            exchange_rate = self.converter.get_rate_for_date(date_str)
            
            # Convert based on input currency
            if currency == 'EUR':
                amount_eur = amount
                amount_usd = amount * exchange_rate
                print(f"   💶 {date_str}: €{amount_eur:,.2f} → ${amount_usd:,.2f} (Rate: {exchange_rate:.4f})")
            elif currency == 'USD':
                amount_usd = amount
                amount_eur = amount / exchange_rate
                print(f"   💵 {date_str}: ${amount_usd:,.2f} → €{amount_eur:,.2f} (Rate: {exchange_rate:.4f})")
            else:
                print(f"   ⚠️  Unbekannte Währung '{currency}' für {date_str}, überspringe...")
                return None
            
            return {
                'timestamp': deposit_date.strftime("%Y-%m-%d %H:%M:%S"),
                'time': deposit_date.strftime("%Y-%m-%d %H:%M:%S"),
                'type': trans_type,
                'amount': amount_usd,
                'usd': amount_usd,
                'amount_eur': amount_eur,
                'description': f"MANUAL: {description}",
                'hash': f"manual_{timestamp}_{trans_type}",
                'exchange_rate': exchange_rate,
                'input_currency': currency,
                'input_amount': amount
            }
            
        except Exception as e:
            print(f"   ❌ Fehler bei Zeile {row.name}: {e}")
            return None
    
    def read_manual_trades(self) -> pd.DataFrame:
        """Read and process manual trades from CSV"""
        if not os.path.exists(self.trades_csv):
            print(f"ℹ️  Keine manuellen Trades gefunden: {self.trades_csv}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(self.trades_csv, encoding='utf-8')
            
            # Filter only enabled entries
            if 'enabled' in df.columns:
                df = df[df['enabled'] == 1]
            
            if df.empty:
                print(f"ℹ️  Keine aktiven Trades in {self.trades_csv}")
                return pd.DataFrame()
            
            print(f"📥 Verarbeite {len(df)} manuelle(n) Trade(s)...")
            
            # Ensure we have exchange rates for all dates
            dates_needed = df['date'].tolist()
            self.converter.ensure_rates_available(dates_needed)
            
            # Process each trade
            processed_trades = []
            for idx, row in df.iterrows():
                trade = self._process_trade_row(row)
                if trade:
                    processed_trades.append(trade)
            
            if processed_trades:
                result_df = pd.DataFrame(processed_trades)
                print(f"✅ {len(processed_trades)} Trade(s) erfolgreich verarbeitet")
                return result_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Fehler beim Lesen von {self.trades_csv}: {e}")
            return pd.DataFrame()
    
    def _process_trade_row(self, row: pd.Series) -> Dict:
        """Process a single trade row with EUR/USD conversion"""
        try:
            # Parse date
            date_str = str(row['date'])
            trade_date = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = int(trade_date.timestamp() * 1000)
            
            # Get trade details
            coin = str(row['coin']).upper()
            side = str(row['side']).lower()
            side_formatted = 'Buy' if side in ['buy', 'b', 'long'] else 'Sell'
            size = float(row['size'])
            price = float(row['price'])
            currency = str(row.get('currency', 'USD')).upper()
            leverage = float(row.get('leverage', 1))
            fee = float(row.get('fee', 0))
            pnl = float(row.get('pnl', 0))
            description = str(row.get('description', 'Manual trade'))
            
            # Get exchange rate for that date
            exchange_rate = self.converter.get_rate_for_date(date_str)
            
            # Convert price based on input currency
            if currency == 'EUR':
                price_eur = price
                price_usd = price * exchange_rate
                print(f"   💶 {date_str}: {side_formatted} {size} {coin} @ €{price_eur:,.2f} (${price_usd:,.2f})")
            elif currency == 'USD':
                price_usd = price
                price_eur = price / exchange_rate
                print(f"   💵 {date_str}: {side_formatted} {size} {coin} @ ${price_usd:,.2f} (€{price_eur:,.2f})")
            else:
                print(f"   ⚠️  Unbekannte Währung '{currency}' für {date_str}, überspringe...")
                return None
            
            # Calculate total value
            total_value_usd = size * price_usd
            
            # Ensure fee is negative
            if fee > 0:
                fee = -abs(fee)
            
            return {
                'timestamp': trade_date.strftime("%Y-%m-%d %H:%M:%S"),
                'time': trade_date.strftime("%Y-%m-%d %H:%M:%S"),
                'coin': coin,
                'side': side_formatted,
                'size': size,
                'price': price_usd,
                'fee': fee,
                'closed_pnl': pnl,
                'direction': f"MANUAL_{side_formatted.upper()}",
                'start_position': 0,
                'hash': f"manual_{timestamp}_{coin}_{side}",
                'oid': f"manual_{timestamp}",
                'leverage': leverage,
                'total_value': total_value_usd,
                'description': f"MANUAL: {description}",
                'exchange_rate': exchange_rate,
                'input_currency': currency,
                'input_price': price
            }
            
        except Exception as e:
            print(f"   ❌ Fehler bei Zeile {row.name}: {e}")
            return None
    
    def print_instructions(self):
        """Print instructions for using the manual input system"""
        print("\n" + "═" * 80)
        print("📝 MANUAL INPUT SYSTEM - ANLEITUNG")
        print("═" * 80)
        print(f"\n📁 Ordner: {self.manual_input_folder}/")
        print(f"📄 Dateien:")
        print(f"   - {os.path.basename(self.deposits_csv)} (Einzahlungen)")
        print(f"   - {os.path.basename(self.trades_csv)} (Trades)")
        print("\n✏️  SO FUNKTIONIERT'S:")
        print("   1. Öffnen Sie die CSV-Dateien in Excel oder einem Texteditor")
        print("   2. Bearbeiten Sie die Beispielzeilen oder fügen Sie neue hinzu")
        print("   3. Speichern Sie die Dateien")
        print("   4. Starten Sie das Programm - Ihre Daten werden automatisch geladen!")
        print("\n💡 WICHTIG:")
        print("   - 'enabled' Spalte: 1 = aktiv, 0 = deaktiviert")
        print("   - 'currency' kann EUR oder USD sein")
        print("   - Datum-Format: YYYY-MM-DD (z.B. 2025-10-18)")
        print("   - EUR↔USD Konvertierung erfolgt automatisch zum Tages-Wechselkurs")
        print("\n🎯 FÜR STEUER RELEVANT:")
        print("   ✅ Einzahlungen (Kapital-Tracking)")
        print("   ✅ Realisierte Gewinne/Verluste aus Trades (Closed PnL)")
        print("   ✅ Trading-Gebühren (steuerlich absetzbar)")
        print("   ✅ Funding Costs (steuerlich absetzbar)")
        print("\n❌ NICHT STEUERRELEVANT:")
        print("   - Abhebungen/Withdrawals (ändern Gewinn nicht)")
        print("   - Unrealisierte Gewinne (offene Positionen)")
        print("═" * 80 + "\n")


def test_manual_input_system():
    """Test the manual input system"""
    handler = ManualInputHandler()
    
    print("🧪 TESTE MANUAL INPUT SYSTEM")
    print("=" * 80)
    
    # Generate templates
    handler.generate_template_csvs()
    
    # Show instructions
    handler.print_instructions()
    
    # Try to read (will be empty first time)
    deposits_df = handler.read_manual_deposits()
    trades_df = handler.read_manual_trades()
    
    print(f"\n📊 ERGEBNIS:")
    print(f"   Einzahlungen: {len(deposits_df)} Einträge")
    print(f"   Trades: {len(trades_df)} Einträge")
    
    if not deposits_df.empty:
        print(f"\n💰 EINZAHLUNGEN:")
        print(deposits_df[['time', 'type', 'usd', 'amount_eur', 'description']].to_string())
    
    if not trades_df.empty:
        print(f"\n📊 TRADES:")
        print(trades_df[['time', 'coin', 'side', 'size', 'price']].to_string())


if __name__ == "__main__":
    test_manual_input_system()
