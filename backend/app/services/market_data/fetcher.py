"""
Data Fetcher Module

Handles downloading and saving historical stock data from Yahoo Finance.
"""

import os
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataFetcher:
    """
    A class for fetching and managing historical stock data from Yahoo Finance.
    
    Attributes:
        data_path (str): Path to the data storage directory.
        default_period (str): Default period for historical data (e.g., '6mo', '1y').
        default_interval (str): Default interval for data points (e.g., '1d', '1h').
    """
    
    def __init__(
        self,
        data_path: str = "data_storage/historical/",
        default_period: str = "6mo",
        default_interval: str = "1d"
    ):
        """
        Initialize the DataFetcher with storage settings.
        
        Args:
            data_path: Directory to store CSV files.
            default_period: Default period for data downloads.
            default_interval: Default interval between data points.
        """
        self.data_path = Path(data_path)
        self.default_period = default_period
        self.default_interval = default_interval
        
        # Create the data directory if it doesn't exist
        self.data_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"DataFetcher initialized. Storage path: {self.data_path}")
    
    def fetch_historical(
        self,
        ticker: str,
        period: Optional[str] = None,
        interval: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch historical stock data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT').
            period: Period to fetch ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max').
            interval: Data interval ('1m', '5m', '15m', '30m', '1h', '1d', '5d', '1wk', '1mo').
            start: Start date in 'YYYY-MM-DD' format.
            end: End date in 'YYYY-MM-DD' format.
        
        Returns:
            pd.DataFrame: Historical OHLCV data for the ticker.
            
        Raises:
            ValueError: If no data is found or parameters are invalid.
            Exception: For download failures.
        """
        # Use defaults if not provided
        period = period or self.default_period
        interval = interval or self.default_interval
        
        logger.info(f"Fetching data for {ticker} | Period: {period} | Interval: {interval}")
        
        try:
            # Validate ticker
            if not ticker or not isinstance(ticker, str):
                raise ValueError(f"Invalid ticker: {ticker}")
            
            # Download data
            if start and end:
                data = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )
            else:
                data = yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )
            
            # Check if data is empty
            if data.empty:
                raise ValueError(f"No data found for ticker: {ticker}")
            
            # Flatten MultiIndex columns if they exist
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = ['_'.join(col).strip() for col in data.columns.values]
            
            # Ensure we have at least 2 rows
            if len(data) < 2:
                logger.warning(f"Only {len(data)} rows downloaded for {ticker}. Data may be insufficient.")
            
            logger.info(f"✅ Successfully fetched {len(data)} rows for {ticker}")
            
            # Add ticker column for reference
            data['Ticker'] = ticker
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {ticker}: {str(e)}")
            raise
    
    def save_to_csv(
        self,
        data: pd.DataFrame,
        ticker: str,
        period: Optional[str] = None,
        interval: Optional[str] = None
    ) -> str:
        """
        Save DataFrame to CSV file with standardized naming.
        
        Args:
            data: DataFrame containing stock data.
            ticker: Stock ticker symbol.
            period: Period used for download (for filename).
            interval: Interval used for download (for filename).
            
        Returns:
            str: Path to the saved file.
        """
        period = period or self.default_period
        interval = interval or self.default_interval
        
        # Generate filename: TICKER_PERIOD_INTERVAL.csv
        filename = f"{ticker.upper()}_{period}_{interval}.csv"
        filepath = self.data_path / filename
        
        try:
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            data.to_csv(filepath, index=True)
            logger.info(f"✅ Data saved to: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Failed to save data to {filepath}: {str(e)}")
            raise
    
    def load_from_csv(
        self,
        ticker: str,
        period: Optional[str] = None,
        interval: Optional[str] = None,
        filepath: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            ticker: Stock ticker symbol.
            period: Period used for download.
            interval: Interval used for download.
            filepath: Direct path to CSV file (overrides constructed path).
            
        Returns:
            pd.DataFrame: Data loaded from CSV.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        if filepath:
            path = Path(filepath)
        else:
            period = period or self.default_period
            interval = interval or self.default_interval
            filename = f"{ticker.upper()}_{period}_{interval}.csv"
            path = self.data_path / filename
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            data = pd.read_csv(path, index_col=0, parse_dates=True)
            logger.info(f"✅ Loaded {len(data)} rows from: {path}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load data from {path}: {str(e)}")
            raise
    
    def fetch_and_save(
        self,
        ticker: str,
        period: Optional[str] = None,
        interval: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> str:
        """
        Combined method to fetch and save data in one call.
        
        Args:
            ticker: Stock ticker symbol.
            period: Period to fetch.
            interval: Data interval.
            start: Start date (overrides period).
            end: End date.
            
        Returns:
            str: Path to the saved file.
        """
        period = period or self.default_period
        interval = interval or self.default_interval
        
        data = self.fetch_historical(ticker, period, interval, start, end)
        
        if not data.empty:
            # Add Ticker column if it doesn't have one
            if 'Ticker' not in data.columns:
                data['Ticker'] = ticker
            
            return self.save_to_csv(data, ticker, period, interval)
        else:
            raise ValueError(f"No data to save for ticker: {ticker}")
    
    def get_available_tickers(self) -> list:
        """
        List all available tickers in the data storage.
        
        Returns:
            list: List of ticker symbols that have saved data.
        """
        tickers = []
        for file in self.data_path.glob("*.csv"):
            # Extract ticker from filename (TICKER_PERIOD_INTERVAL.csv)
            parts = file.stem.split('_')
            if parts:
                tickers.append(parts[0])
        return sorted(set(tickers))
    
    def get_data_summary(self, ticker: str) -> dict:
        """
        Get summary information for a ticker's data.
        
        Args:
            ticker: Stock ticker symbol.
            
        Returns:
            dict: Summary information including date range, rows, columns.
        """
        try:
            data = self.load_from_csv(ticker)
            return {
                'ticker': ticker,
                'rows': len(data),
                'columns': list(data.columns),
                'date_range': (data.index.min(), data.index.max()),
                'start_date': data.index.min().strftime('%Y-%m-%d'),
                'end_date': data.index.max().strftime('%Y-%m-%d'),
                'has_volume': 'Volume' in data.columns,
                'has_close': 'Close' in data.columns
            }
        except FileNotFoundError:
            return {'ticker': ticker, 'error': 'No data found'}
        except Exception as e:
            return {'ticker': ticker, 'error': str(e)}

# ====== Quick test function ======
def main():
    """Test the DataFetcher class."""
    print("🧪 Testing DataFetcher...\n")
    
    # Initialize fetcher
    fetcher = DataFetcher()
    
    # Test fetch
    print("📊 Downloading AAPL data...")
    df = fetcher.fetch_historical("AAPL", period="1mo")
    print(f"✅ Downloaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}\n")
    
    # Test save
    print("💾 Saving data...")
    filepath = fetcher.save_to_csv(df, "AAPL", period="1mo")
    print(f"✅ Saved to: {filepath}\n")
    
    # Test load
    print("📖 Loading data...")
    df_loaded = fetcher.load_from_csv("AAPL", period="1mo")
    print(f"✅ Loaded {len(df_loaded)} rows\n")
    
    # Test summary
    print("📊 Data summary:")
    summary = fetcher.get_data_summary("AAPL")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests passed! DataFetcher is ready.")


if __name__ == "__main__":
    main()