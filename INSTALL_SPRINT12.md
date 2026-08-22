# NPAT Sprint 12 Final Package

This package is a **source-code overlay** for the existing `C:\NPAT` project.

## Safe update

1. Keep your existing `C:\NPAT\.env` and `data\storage` files.
2. Back up the current project first, or create a Git commit.
3. Extract this package over `C:\NPAT` and allow source files to be replaced.
4. Do **not** replace your `.env` or paper-trading storage/history files.
5. From `C:\NPAT` run:

```powershell
python -m pytest tests\paper_trading -q --basetemp=C:\NPAT\.pytest_tmp
python -m pytest tests\test_risk_engine.py tests\test_trade_planner.py tests\test_backtest_engine.py tests\test_constituent_loader.py -q --basetemp=C:\NPAT\.pytest_tmp
streamlit run app.py
```

## What is included

- Sprint 8–12 risk, trade-planning, backtesting and safety modules.
- Compact sector-strength dashboard.
- Selected-index gainers/losers for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX and BANKEX.
- Future BUY/SELL candidate with protective option hedge.
- Individual-stock BUY/SELL candidate with protective stock-option hedge when provider data supports it.
- Sprint 12 final documentation and tests.
- Existing paper-trading code and tests from the supplied current project.

## Safety

The new planner is **paper/review only**. No live broker order placement was added.

Sprint 12 is the final planned development milestone. Future changes should be maintenance, data-reference refreshes, bug fixes and controlled strategy tuning.
