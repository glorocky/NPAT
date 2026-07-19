"""
=========================================================
NPAT - Configuration Module
=========================================================

Purpose
-------
Central configuration for the entire application.

All modules must read settings from this file.
No hardcoded values are allowed outside this module.

Author:
Rocky Chopra

Version:
1.0.0
=========================================================
"""

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

CORE_DIR = PROJECT_ROOT / "core"

UI_DIR = PROJECT_ROOT / "ui"

SERVICES_DIR = PROJECT_ROOT / "services"

UTILS_DIR = PROJECT_ROOT / "utils"

TESTS_DIR = PROJECT_ROOT / "tests"


# =========================================================
# APPLICATION SETTINGS
# =========================================================

APP_NAME = "NIFTY PRO AI TERMINAL"

APP_VERSION = "1.0.0"

DEBUG_MODE = True

AUTO_REFRESH_SECONDS = 5

DEFAULT_INDEX = "NIFTY"

DEFAULT_THEME = "dark"

DEFAULT_TIMEFRAME = "1m"


# =========================================================
# MARKET SETTINGS
# =========================================================

RISK_FREE_RATE = 0.07

# =========================================================
# CONTRACT SPECIFICATIONS
# =========================================================

LOT_SIZES = {
    "NIFTY": 65,
    "BANKNIFTY": 35,      # Update if NSE revises
    "FINNIFTY": 65,
    "MIDCPNIFTY": 120,
}

NIFTY_STRIKE_STEP = 50

BANKNIFTY_STRIKE_STEP = 100

# =========================================================
# HTTP SETTINGS
# =========================================================

HTTP_TIMEOUT = 15

HTTP_RETRIES = 3

HTTP_RETRY_DELAY = 2

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)

# =========================================================
# DATA PROVIDER
# =========================================================

DEFAULT_DATA_PROVIDER = "YAHOO"

ENABLE_NSE = True

ENABLE_YAHOO = True

ENABLE_GROWW = False
# =========================================================
# DASHBOARD SETTINGS
# =========================================================

ATM_STRIKE_COUNT = 3

SHOW_GREEKS = True

SHOW_AI_PANEL = True

SHOW_HEATMAP = True

SHOW_FUTURES = True

SHOW_PARTICIPANTS = True


# =========================================================
# SHOONYA CONFIGURATION
# =========================================================

@dataclass
class ShoonyaConfig:

    user_id: str = os.getenv("SHOONYA_USER_ID", "")

    password: str = os.getenv("SHOONYA_PASSWORD", "")

    api_key: str = os.getenv("SHOONYA_API_KEY", "")

    totp_secret: str = os.getenv("SHOONYA_TOTP_SECRET", "")

    vendor_code: str = os.getenv("SHOONYA_VENDOR_CODE", "")

    imei: str = "NPAT-TERMINAL"
    
    timeout: int = HTTP_TIMEOUT

SHOONYA = ShoonyaConfig()


# =========================================================
# WEBSOCKET SETTINGS
# =========================================================

ENABLE_WEBSOCKET = True

RECONNECT_INTERVAL = 5


# =========================================================
# AI SETTINGS
# =========================================================

AI_CONFIDENCE_THRESHOLD = 70

ENABLE_AI_SIGNALS = True

ENABLE_AI_REASONING = True


# =========================================================
# LOGGING
# =========================================================

LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "npat.log"