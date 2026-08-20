# NPAT Sprint-7 Index + Contract Selection Patch

Baseline: `sprint-7-dashboard` / `719e21a`

This package updates the NPAT branch for:

- NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
- SENSEX (BSE)
- BANKEX (BSE)
- selected-index routing from the sidebar into MarketService
- actual AI option strike/premium display
- expiry-day Zero-to-Hero scanning from 13:00-13:30 IST
- existing Black-Scholes/forward premium data as a selection input
- no live Groww order placement

Run from `C:\NPAT`:

```powershell
python apply_patch.py
streamlit run app.py
```

The installer creates a backup under `.npat_patch_backup` and runs `py_compile`.
