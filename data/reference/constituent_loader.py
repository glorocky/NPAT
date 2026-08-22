"""Reference constituent loader for the index selected in the terminal."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REFERENCE_DIR = Path(__file__).resolve().parent
NIFTY50_FILE = REFERENCE_DIR / "nifty50_constituents_raw.csv"

# Reference universe for the major derivatives/index views supported by NPAT.
# Membership can change after index rebalances; the loader intentionally keeps
# this table separate so it can be refreshed without changing analytics code.
INDEX_SYMBOLS: dict[str, list[str]] = {
    "BANKNIFTY": ["HDFCBANK","ICICIBANK","AXISBANK","SBIN","KOTAKBANK","FEDERALBNK","INDUSINDBK","AUBANK","BANKBARODA","IDFCFIRSTB","CANBK","PNB","BANDHANBNK","YESBANK"],
    "FINNIFTY": ["HDFCBANK","ICICIBANK","AXISBANK","SBIN","KOTAKBANK","BAJFINANCE","BAJAJFINSV","HDFCLIFE","SBILIFE","SHRIRAMFIN","CHOLAFIN","PFC","RECLTD","MUTHOOTFIN","HDFCAMC","ICICIPRULI","JIOFIN","LICI","ICICIGI","MOTILALOFS","MANAPPURAM","PEL","ABCAPITAL","CANBK","BANKBARODA"],
    "MIDCPNIFTY": ["ASHOKLEY","AUROPHARMA","BHEL","CGPOWER","CUMMINSIND","DIXON","FEDERALBNK","FORTIS","GODREJPROP","HINDPETRO","IDFCFIRSTB","INDHOTEL","INDUSTOWER","JINDALSTEL","LUPIN","MPHASIS","NMDC","OFSS","PAGEIND","PERSISTENT","POLYCAB","RECLTD","SAIL","SRF","TRENT"],
    "SENSEX": ["RELIANCE","HDFCBANK","ICICIBANK","BHARTIARTL","TCS","INFY","SBIN","AXISBANK","LARSEN","ITC","KOTAKBANK","M&M","BAJFINANCE","HINDUNILVR","MARUTI","SUNPHARMA","TATASTEEL","NTPC","POWERGRID","ULTRACEMCO","HCLTECH","TITAN","ASIANPAINT","ADANIPORTS","BEL","TECHM","INDUSINDBK","ETERNAL","TATAMOTORS","TRENT"],
    "BANKEX": ["HDFCBANK","ICICIBANK","AXISBANK","SBIN","KOTAKBANK","INDUSINDBK","BANKBARODA","FEDERALBNK","AUBANK","IDFCFIRSTB"],
}


def _normalise(df: pd.DataFrame, exchange: str) -> pd.DataFrame:
    out = df.copy()
    out["symbol"] = out["symbol"].astype(str).str.strip().str.upper()
    out["exchange"] = exchange
    if "company_name" not in out:
        out["company_name"] = out["symbol"]
    if "sector" not in out:
        out["sector"] = "Index Constituent"
    return out[["symbol", "company_name", "sector", "exchange"]].drop_duplicates("symbol").reset_index(drop=True)


class ConstituentLoader:
    @classmethod
    def load_nifty50(cls) -> pd.DataFrame:
        df = pd.read_csv(NIFTY50_FILE)
        required = {"Company Name", "Industry", "Symbol"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"NIFTY 50 constituent file missing: {sorted(missing)}")
        result = df[["Symbol", "Company Name", "Industry"]].rename(columns={"Symbol":"symbol","Company Name":"company_name","Industry":"sector"})
        return _normalise(result, "NSE")

    @classmethod
    def load_for_index(cls, symbol: str, exchange: str = "NSE") -> pd.DataFrame:
        symbol = symbol.upper().strip()
        if symbol == "NIFTY":
            return cls.load_nifty50()
        symbols = INDEX_SYMBOLS.get(symbol)
        if not symbols:
            return pd.DataFrame(columns=["symbol","company_name","sector","exchange"])
        # Reuse NIFTY sector labels where available; other members get a neutral label.
        try:
            nifty = cls.load_nifty50().set_index("symbol")
        except Exception:
            nifty = pd.DataFrame()
        rows = []
        for s in symbols:
            sector = "Index Constituent"
            company = s
            if not nifty.empty and s in nifty.index:
                sector = str(nifty.loc[s, "sector"])
                company = str(nifty.loc[s, "company_name"])
            rows.append({"symbol": s, "company_name": company, "sector": sector})
        return _normalise(pd.DataFrame(rows), "BSE" if symbol in {"SENSEX","BANKEX"} else exchange)
