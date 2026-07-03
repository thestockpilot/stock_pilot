"""
Feature Engineering Module

Calculates technical indicators and creates feature matrix from raw stock data.

This module provides a comprehensive feature engineering pipeline for stock data,
including moving averages, RSI, MACD, Bollinger Bands, volume indicators,
volatility measures, and price position indicators.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, List, Dict, Tuple
from ta import add_all_ta_features
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice,MFIIndicator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler('logs/feature_engine.log')  # Save to file
    ]
)

# Create logger instance for this module
logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    Feature engineering class for calculating technical indicators.
    
    This class provides methods to calculate various technical indicators
    from raw OHLCV (Open, High, Low, Close, Volume) stock data.
    
    Attributes:
        data (pd.DataFrame): Raw OHLCV data.
        features (pd.DataFrame): Calculated feature DataFrame.
        feature_columns (List[str]): List of feature column names.
    """
    
    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialize FeatureEngine with optional data.
        
        Args:
            data: Raw OHLCV data with columns: Open, High, Low, Close, Volume.
        """
        self.data = data
        self.features = None
        self.feature_columns = []
        logger.info("FeatureEngine initialized")
        
        if data is not None:
            self.validate_data(data)
    
    # ============================================================
    # DATA VALIDATION
    # ============================================================
    
    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate that data has required columns and sufficient rows.
        
        Args:
            data: DataFrame to validate.
            
        Raises:
            ValueError: If required columns are missing or data is insufficient.
        """
        logger.info("Validating data...")
        
        # Check if data is empty
        if data.empty:
            logger.error("Data is empty")
            raise ValueError("Data cannot be empty")
        
        # Handle MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            logger.info("Detected MultiIndex columns. Flattening...")
            logger.info(f"Before flattening: {data.columns}")
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            logger.info(f"After flattening: {list(data.columns)}")
        
        # Log current columns before renaming
        logger.info(f"Current columns: {list(data.columns)}")
        
        # Define required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = []
        
        # Check each required column
        for required_col in required_columns:
            # If column already exists, we're good
            if required_col in data.columns:
                logger.debug(f"✅ Required column '{required_col}' already exists")
                continue
            
            # If not, look for a column that ends with the required name
            logger.debug(f"Looking for column ending with '{required_col}'...")
            found = False
            
            for col in data.columns:
                # Check if column ends with required name (e.g., 'Close_AAPL' ends with 'Close')
                if col.endswith(required_col):
                    logger.info(f"🔄 Renaming '{col}' to '{required_col}'")
                    data.rename(columns={col: required_col}, inplace=True)
                    found = True
                    break
                
                # Check if column starts with required name (e.g., 'AAPL_Close' starts with 'Close')
                if col.startswith(required_col + '_') or col.startswith(required_col + '.'):
                    logger.info(f"🔄 Renaming '{col}' to '{required_col}' (prefix match)")
                    data.rename(columns={col: required_col}, inplace=True)
                    found = True
                    break
            
            # If not found, add to missing list
            if not found:
                logger.warning(f"❌ Required column '{required_col}' not found")
                missing_columns.append(required_col)
        
        # If we have missing columns, try case-insensitive matching
        if missing_columns:
            logger.info("Attempting case-insensitive matching for missing columns...")
            for missing_col in missing_columns.copy():
                for col in data.columns:
                    if col.lower() == missing_col.lower():
                        logger.info(f"🔄 Renaming '{col}' to '{missing_col}' (case-insensitive)")
                        data.rename(columns={col: missing_col}, inplace=True)
                        missing_columns.remove(missing_col)
                        break
        
        # Final check for missing columns
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.error(f"Available columns: {list(data.columns)}")
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check if there are enough rows
        if len(data) < 14:
            logger.error(f"Insufficient data: {len(data)} rows. Need at least 14.")
            raise ValueError(f"Insufficient data: {len(data)} rows. Need at least 14.")
        
        # Log success
        logger.info(f"✅ Data validated successfully: {len(data)} rows, {len(data.columns)} columns")
        logger.info(f"Columns: {list(data.columns)}")
        
        # Store validated data
        self.data = data
    
    # ============================================================
    # MOVING AVERAGES
    # ============================================================
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Simple and Exponential Moving Averages.
        
        Args:
            data: DataFrame with 'Close' column.
            
        Returns:
            pd.DataFrame: DataFrame with MA features added.
        """
        df = data.copy()
        logger.info("Calculating moving averages...")
        
        # Define periods
        periods = [5, 10, 20, 50, 200]
        
        for period in periods:
            # Simple Moving Average
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
            logger.debug(f"Calculated SMA_{period}")
            
            # Exponential Moving Average
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
            logger.debug(f"Calculated EMA_{period}")
        
        logger.info("✅ Moving averages calculated")
        return df
    
    # ============================================================
    # RSI (RELATIVE STRENGTH INDEX)
    # ============================================================
    
    def calculate_rsi(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI (Relative Strength Index).
        
        Args:
            data: DataFrame with 'Close' column.
            
        Returns:
            pd.DataFrame: DataFrame with RSI_14 column added.
        """
        df = data.copy()
        logger.info("Calculating RSI...")
        
        df['RSI_14'] = RSIIndicator(df['Close'], window=14).rsi()
        
        logger.info("✅ RSI calculated")
        return df
    
    # ============================================================
    # MACD (MOVING AVERAGE CONVERGENCE DIVERGENCE)
    # ============================================================
    
    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: DataFrame with 'Close' column.
            
        Returns:
            pd.DataFrame: DataFrame with MACD, Signal, Histogram columns added.
        """
        df = data.copy()
        logger.info("Calculating MACD...")
        
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        logger.info("✅ MACD calculated")
        return df
    
    # ============================================================
    # BOLLINGER BANDS
    # ============================================================
    
    def calculate_bollinger_bands(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: DataFrame with 'Close' column.
            
        Returns:
            pd.DataFrame: DataFrame with Bollinger Bands columns added.
        """
        df = data.copy()
        logger.info("Calculating Bollinger Bands...")
        
        bb = BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Mid'] = bb.bollinger_mavg()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Width'] = bb.bollinger_wband()
        df['BB_Position'] = bb.bollinger_pband()
        
        logger.info("✅ Bollinger Bands calculated")
        return df
    
    # ============================================================
    # VOLUME INDICATORS
    # ============================================================
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volume indicators.
        
        Args:
            data: DataFrame with 'Close', 'High', 'Low', 'Volume' columns.
            
        Returns:
            pd.DataFrame: DataFrame with volume indicators added.
        """
        df = data.copy()
        logger.info("Calculating Volume indicators...")
        
        # VWAP (Volume Weighted Average Price)
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        # OBV (On-Balance Volume)
        df['OBV'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
        
        # Volume Ratio (current volume / average volume)
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # MFI (Money Flow Index) - using MFIIndicator from ta.volume
        mfi = MFIIndicator(
            high=df['High'], 
            low=df['Low'], 
            close=df['Close'], 
            volume=df['Volume'], 
            window=14
        )
        df['MFI_14'] = mfi.money_flow_index()
        
        logger.info("✅ Volume indicators calculated")
        return df
    
    # ============================================================
    # VOLATILITY INDICATORS
    # ============================================================
    
    def calculate_volatility(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volatility indicators.
        
        Args:
            data: DataFrame with 'Open', 'High', 'Low', 'Close' columns.
            
        Returns:
            pd.DataFrame: DataFrame with volatility indicators added.
        """
        df = data.copy()
        logger.info("Calculating Volatility indicators...")
        
        # ATR (Average True Range)
        df['ATR_14'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
        
        # Daily Return
        df['Daily_Return'] = df['Close'].pct_change()
        
        # Rolling Volatility (20-day)
        df['Volatility_20'] = df['Daily_Return'].rolling(20).std()
        
        # High-Low Ratio
        df['High_Low_Ratio'] = df['High'] / df['Low']
        
        # Close-Open Ratio
        df['Close_Open_Ratio'] = df['Close'] / df['Open']
        
        logger.info("✅ Volatility indicators calculated")
        return df
    
    # ============================================================
    # PRICE POSITION INDICATORS
    # ============================================================
    
    def calculate_price_position(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Price Position and Momentum indicators.
        
        Args:
            data: DataFrame with 'Close', 'High', 'Low', 'SMA_20', 'SMA_50' columns.
            
        Returns:
            pd.DataFrame: DataFrame with price position features added.
        """
        df = data.copy()
        logger.info("Calculating Price Position indicators...")
        
        # Price Position in 20-day range (0 to 1)
        # 0 = at 20-day low, 1 = at 20-day high
        low_20 = df['Low'].rolling(20).min()
        high_20 = df['High'].rolling(20).max()
        df['Price_Position'] = (df['Close'] - low_20) / (high_20 - low_20)
        logger.debug("Calculated Price_Position")
        
        # Rate of Change (ROC) - 10-day momentum
        # Positive = upward momentum, Negative = downward momentum
        df['ROC_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
        logger.debug("Calculated ROC_10")
        
        # Price relative to moving averages
        # > 1 = above average (bullish), < 1 = below average (bearish)
        df['Price_to_SMA_20'] = df['Close'] / df['SMA_20']
        df['Price_to_SMA_50'] = df['Close'] / df['SMA_50']
        logger.debug("Calculated Price_to_SMA_20 and Price_to_SMA_50")
        
        # Simple trend direction signal
        # 1 if price above 20-day SMA, else 0
        df['Price_Above_SMA'] = (df['Close'] > df['SMA_20']).astype(int)
        logger.debug("Calculated Price_Above_SMA")
        
        logger.info("✅ Price Position indicators calculated")
        return df
    
    # ============================================================
    # NAN HANDLING
    # ============================================================
    
    def handle_nan_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle NaN values in feature DataFrame.
        
        Args:
            df: DataFrame with potential NaN values.
            
        Returns:
            pd.DataFrame: Cleaned DataFrame with no NaN values.
        """
        logger.info("Handling NaN values...")
        
        initial_rows = len(df)
        
        # Forward fill then backward fill, then drop any remaining NaNs
        df = df.ffill().bfill().dropna()
        
        removed_rows = initial_rows - len(df)
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} rows with NaN values")
        else:
            logger.info("No NaN values found")
        
        logger.info(f"Final shape: {df.shape}")
        return df
    
    # ============================================================
    # MASTER METHOD - CALCULATE ALL FEATURES
    # ============================================================
    
    def calculate_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators in one pipeline.
        
        This method runs all feature calculation methods in sequence,
        producing a complete feature matrix ready for ML models.
        
        Args:
            data: Raw OHLCV DataFrame.
            
        Returns:
            pd.DataFrame: Complete feature matrix with all indicators.
        """
        logger.info("Starting full feature engineering pipeline...")
        
        # Step 1: Validate data
        self.validate_data(data)
        df = self.data.copy()
        
        # Step 2: Calculate all features in sequence
        df = self.calculate_moving_averages(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_volume_indicators(df)
        df = self.calculate_volatility(df)
        df = self.calculate_price_position(df)
        
        # Step 3: Handle NaN values
        df = self.handle_nan_values(df)
        
        # Step 4: Store results
        self.features = df
        base_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']
        self.feature_columns = [col for col in df.columns if col not in base_cols]
        
        logger.info(f"✅ All features calculated: {len(self.feature_columns)} features")
        logger.info(f"Feature columns: {self.feature_columns}")
        
        return df
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def get_feature_names(self) -> List[str]:
        """
        Return list of feature column names.
        
        Returns:
            List[str]: List of feature column names.
        """
        return self.feature_columns
    
    def get_feature_summary(self) -> pd.DataFrame:
        """
        Return summary statistics for features.
        
        Returns:
            pd.DataFrame: Summary statistics (count, mean, std, min, max, etc.)
        """
        if self.features is None:
            logger.warning("No features available. Run calculate_all_features() first.")
            return pd.DataFrame()
        
        if not self.feature_columns:
            logger.warning("No feature columns found.")
            return pd.DataFrame()
        
        return self.features[self.feature_columns].describe()
    
    def get_feature_correlation(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix between features.
        
        Args:
            method: Correlation method ('pearson', 'kendall', 'spearman').
            
        Returns:
            pd.DataFrame: Correlation matrix.
        """
        if self.features is None:
            logger.warning("No features available. Run calculate_all_features() first.")
            return pd.DataFrame()
        
        if not self.feature_columns:
            logger.warning("No feature columns found.")
            return pd.DataFrame()
        
        return self.features[self.feature_columns].corr(method=method)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Placeholder for feature importance calculation.
        
        This will be implemented in the ML module after model training.
        
        Returns:
            Dict[str, float]: Feature importance scores.
        """
        logger.warning("Feature importance not available until model is trained.")
        return {}


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    """Quick test to verify the class works."""
    from src.data.fetcher import DataFetcher
    
    print("=" * 60)
    print("🧪 Quick Test: FeatureEngine")
    print("=" * 60)
    
    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_historical("AAPL", period="6mo")
    
    # Create engine and calculate features
    engine = FeatureEngine()
    df = engine.calculate_all_features(data)
    
    print(f"\n📊 Final shape: {df.shape}")
    print(f"📊 Features: {len(engine.feature_columns)}")
    print(f"📊 Feature columns: {engine.feature_columns[:10]}...")
    
    # Show summary
    print("\n📊 Feature Summary:")
    print(engine.get_feature_summary().head())
    
    print("\n✅ FeatureEngine ready!")