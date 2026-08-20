cd C:\NPAT
git status
git diff --stat
git diff -- app.py dashboard/sidebar.py dashboard/components/ai_panel.py ai/option_selector.py ai/zero_to_hero.py services/ai_service.py services/market_service.py
# If the diff and Streamlit result are good:
# git add app.py dashboard/sidebar.py dashboard/components/ai_panel.py ai/option_selector.py ai/zero_to_hero.py services/ai_service.py services/market_service.py
# git commit -m "Sprint 7: multi-index and expiry option selection"
# git push
