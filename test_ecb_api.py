"""
Test script for ECB Statistical Data API
"""

import requests
import pandas as pd
import io

def test_ecb_api():
    base_url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
    params = {
        "format": "csvdata",
        "startPeriod": "2024-09-01",
        "endPeriod": "2024-09-25"
    }
    
    print("🌐 Testing ECB Statistical Data API...")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.text)} bytes")
        
        # Parse CSV response
        df = pd.read_csv(io.StringIO(response.text))
        print(f"📊 DataFrame shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show first few rows
        print("\n🔍 First 5 rows:")
        print(df.head())
        
        # Process rates
        rates_data = {}
        
        for _, row in df.iterrows():
            if pd.notna(row.get('OBS_VALUE')):
                date = row['TIME_PERIOD']
                # ECB gives USD per 1 EUR, we want to convert USD to EUR so we need 1/rate
                usd_per_eur = float(row['OBS_VALUE'])
                eur_per_usd = 1.0 / usd_per_eur
                rates_data[date] = eur_per_usd
                print(f"📅 {date}: {usd_per_eur} USD per EUR -> {eur_per_usd:.6f} EUR per USD")
        
        print(f"\n✅ Successfully processed {len(rates_data)} exchange rates")
        return rates_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    rates = test_ecb_api()
    print(f"\n📊 Final rates dictionary: {rates}")
