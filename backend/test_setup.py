"""
StockPilot - Environment Test Script
Verifies all dependencies are correctly installed.
"""

import sys

# List of required packages
packages = [
    'numpy',
    'pandas',
    'yfinance',
    'ta',
    'matplotlib',
    'seaborn',
    'xgboost',
    'sklearn',
    'joblib',
    'fastapi',
    'uvicorn',
    'websockets',
    'pydantic',
    'dotenv',
    'pytest',
    'structlog',
    'jupyterlab',
]

print("🔍 Verifying StockPilot environment...\n")
print(f"Python version: {sys.version}\n")

missing = []
installed = []

for pkg in packages:
    try:
        __import__(pkg)
        installed.append(pkg)
        print(f"✅ {pkg} - OK")
    except ImportError as e:
        missing.append(pkg)
        print(f"❌ {pkg} - MISSING ({e})")

print("\n" + "="*60)
print(f"✅ Installed: {len(installed)}/{len(packages)}")
if missing:
    print(f"❌ Missing: {len(missing)}/{len(packages)}")
    print("\nInstall missing packages with:")
    for pkg in missing:
        print(f"   uv pip install {pkg}")
else:
    print("🎉 All packages are installed! Environment is ready.")

# Additional test: yfinance data fetch
print("\n📊 Testing yfinance data download...")
try:
    import yfinance as yf
    data = yf.download("AAPL", period="5d", progress=False)
    print(f"✅ Downloaded {len(data)} trading days of AAPL data")
    # ✅ FIX: Use .item() to extract scalar value from pandas Series
    latest_price = data['Close'].iloc[-1].item()
    print(f"   Latest close: ${latest_price:.2f}")
    print("✅ yfinance is working correctly.")
except Exception as e:
    print(f"❌ yfinance test failed: {e}")

print("\n✅ Environment check complete. You're ready to start Day 2!")