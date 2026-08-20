from pathlib import Path
import py_compile

files = [
    "app.py",
    "dashboard/sidebar.py",
    "dashboard/components/ai_panel.py",
    "ai/option_selector.py",
    "ai/zero_to_hero.py",
    "services/ai_service.py",
    "services/market_service.py",
]

for name in files:
    path = Path.cwd() / name
    if not path.exists():
        raise SystemExit(f"MISSING: {name}")
    py_compile.compile(str(path), doraise=True)
    print(f"PASS: {name}")

print("All patch files compile successfully.")
