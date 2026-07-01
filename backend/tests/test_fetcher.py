"""
Test script for DataFetcher class.
Place this file in the tests/ directory.
Run with: python -m tests.test_fetcher
"""

import sys
from pathlib import Path

# Add the project root to Python path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.fetcher import DataFetcher


def test_fetcher():
    """Test DataFetcher functionality."""
    print("🧪 Testing DataFetcher...\n")
    
    fetcher = DataFetcher()
    
    # 1. Download data
    print("📊 Downloading AAPL data...")
    df = fetcher.fetch_historical("AAPL", period="1mo")
    print(f"✅ Downloaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}\n")
    
    # 2. Save to CSV
    print("💾 Saving data...")
    filepath = fetcher.save_to_csv(df, "AAPL", period="1mo")
    print(f"✅ Saved to: {filepath}\n")
    
    # 3. Load from CSV
    print("📖 Loading data...")
    df_loaded = fetcher.load_from_csv("AAPL", period="1mo")
    print(f"✅ Loaded {len(df_loaded)} rows\n")
    
    # 4. Check available tickers
    print("📁 Available tickers:")
    tickers = fetcher.get_available_tickers()
    print(f"   {tickers}\n")
    
    # 5. Get summary
    print("📊 Data summary:")
    summary = fetcher.get_data_summary("AAPL")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests passed! DataFetcher is ready.")


if __name__ == "__main__":
    test_fetcher()