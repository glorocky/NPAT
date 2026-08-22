# NPAT Sprint 8–12 Final Delivery

## Delivered

- Risk engine with stop-distance position sizing, risk/reward gate and exposure gate.
- Future BUY/SELL planning with protective option hedge selection.
- Individual-stock BUY/SELL candidate selection from the currently selected index.
- Protective stock-option hedge when the provider exposes a usable stock option chain.
- Selected-index constituent heatmap: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX and BANKEX.
- Compact sector table replacing the previous tall card-per-sector layout.
- Deterministic backtesting harness and trade evaluation metrics.
- Paper-only kill switch and explicit no-live-order safety boundary.
- Streamlit `use_container_width` deprecation cleanup in updated components.

## Safety boundary

The trade planner creates reviewable recommendations only. It never submits a live order. A protective hedge is shown only when a valid option contract can be resolved from provider data.

## Final milestone

Sprint 12 is the final planned development sprint. Future work is maintenance, data-reference refreshes, bug fixes and measured strategy improvements rather than further architectural expansion.
