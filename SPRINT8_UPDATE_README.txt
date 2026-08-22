NPAT SPRINT 8 UPDATE
====================

Replace the files in this ZIP into your existing C:\NPAT project, keeping the folder structure.

Changes:
1. Sector Strength is now a compact ranked table instead of large repeated KPI cards.
2. Heatmap/Top Gainers/Top Losers now follow the selected index instead of always loading NIFTY 50.
   Supported reference sets: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, BANKEX.
3. Added AI Stock / Futures Trade Planner.
4. Stock plan: BUY/SELL/WAIT based on price momentum plus selected-index regime context.
5. Futures plan: BUY/SELL/WAIT using price, OI positioning, quantity imbalance and market context.
6. Protective hedge logic:
   - Long stock/future -> BUY PUT
   - Short stock/future -> BUY CALL
   Hedge contract is selected from the available option chain and sized using the option lot size.
7. Added tests for index constituent routing and stock/futures hedge planning.
8. Sidebar version updated to v0.5.0 and Sprint 8 / 12.

Verification performed on the new Sprint 8 functionality:
7 targeted tests passed.

Important:
The uploaded project contains unrelated pre-existing test/import/syntax problems outside this Sprint 8 change set. Those were not silently modified. Run your normal full project test suite in your C:\NPAT venv after replacing these files.

This is Sprint 8. Sprint 12 remains the final planned development sprint.
