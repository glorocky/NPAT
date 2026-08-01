"""
=========================================================
NPAT - Constituent Loader

Loads index constituent reference data used by analytics
and dashboard layers.

The loader keeps reference-data handling separate from
providers, analytics and service orchestration.
=========================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# =====================================================
# Reference Paths
# =====================================================

REFERENCE_DIR = Path(__file__).resolve().parent

NIFTY50_FILE = (
    REFERENCE_DIR / "nifty50_constituents_raw.csv"
)


# =====================================================
# Constituent Loader
# =====================================================

class ConstituentLoader:
    """
    Load and validate index constituent reference data.
    """

    # -------------------------------------------------
    # NIFTY 50
    # -------------------------------------------------

    @classmethod
    def load_nifty50(cls) -> pd.DataFrame:
        """
        Load the official NIFTY 50 constituent master.

        Returns a normalized DataFrame containing:

        symbol
        company_name
        sector
        exchange
        series
        isin
        """

        if not NIFTY50_FILE.exists():
            raise FileNotFoundError(
                f"NIFTY 50 constituent file not found: "
                f"{NIFTY50_FILE}"
            )

        df = pd.read_csv(NIFTY50_FILE)

        required_columns = {
            "Company Name",
            "Industry",
            "Symbol",
            "Series",
            "ISIN Code",
        }

        missing_columns = (
            required_columns - set(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "NIFTY 50 constituent file is missing "
                f"columns: {sorted(missing_columns)}"
            )

        # ---------------------------------------------
        # Normalize
        # ---------------------------------------------

        result = df[
            [
                "Symbol",
                "Company Name",
                "Industry",
                "Series",
                "ISIN Code",
            ]
        ].copy()

        result.rename(
            columns={
                "Symbol": "symbol",
                "Company Name": "company_name",
                "Industry": "sector",
                "Series": "series",
                "ISIN Code": "isin",
            },
            inplace=True,
        )

        result["symbol"] = (
            result["symbol"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        result["exchange"] = "NSE"

        # ---------------------------------------------
        # Validate
        # ---------------------------------------------

        if result["symbol"].duplicated().any():
            duplicates = (
                result.loc[
                    result["symbol"].duplicated(),
                    "symbol",
                ]
                .tolist()
            )

            raise ValueError(
                "Duplicate NIFTY 50 symbols found: "
                f"{duplicates}"
            )

        if len(result) != 50:
            raise ValueError(
                "Expected 50 NIFTY constituents, "
                f"received {len(result)}."
            )

        return result[
            [
                "symbol",
                "company_name",
                "sector",
                "exchange",
                "series",
                "isin",
            ]
        ].reset_index(drop=True)