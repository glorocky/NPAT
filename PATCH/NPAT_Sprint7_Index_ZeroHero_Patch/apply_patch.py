from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path.cwd()

OVERLAY = {
    "app.py": ROOT / "app.py",
    "dashboard/sidebar.py": ROOT / "dashboard/sidebar.py",
    "dashboard/components/ai_panel.py": ROOT / "dashboard/components/ai_panel.py",
    "ai/option_selector.py": ROOT / "ai/option_selector.py",
    "ai/zero_to_hero.py": ROOT / "ai/zero_to_hero.py",
    "services/ai_service.py": ROOT / "services/ai_service.py",
}


def fail(message: str) -> None:
    raise SystemExit(f"\nERROR: {message}\n")


def backup(path: Path, backup_root: Path) -> None:
    if not path.exists():
        fail(f"Required file not found: {path}")
    destination = backup_root / path.relative_to(REPO)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def patch_market_service() -> None:
    path = REPO / "services" / "market_service.py"
    text = path.read_text(encoding="utf-8")

    replacements = [
        (
            '''vix_quote = self.provider.get_quote(\n            trading_symbol="INDIAVIX",\n            exchange=exchange,\n            segment="CASH",\n        )''',
            '''vix_quote = self.provider.get_quote(\n            trading_symbol="INDIAVIX",\n            exchange="NSE",\n            segment="CASH",\n        )''',
        ),
        (
            '''heatmap_ltp = self.provider.get_ltp_batch(\n            symbols=constituent_symbols,\n            exchange=exchange,\n            segment="CASH",\n        )''',
            '''heatmap_ltp = self.provider.get_ltp_batch(\n            symbols=constituent_symbols,\n            exchange="NSE",\n            segment="CASH",\n        )''',
        ),
        (
            '''heatmap_ohlc = self.provider.get_ohlc_batch(\n            symbols=constituent_symbols,\n            exchange=exchange,\n            segment="CASH",\n        )''',
            '''heatmap_ohlc = self.provider.get_ohlc_batch(\n            symbols=constituent_symbols,\n            exchange="NSE",\n            segment="CASH",\n        )''',
        ),
    ]

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            fail("MarketService expected block not found; patch stopped safely.")

    path.write_text(text, encoding="utf-8")


def compile_check() -> None:
    targets = [
        REPO / "app.py",
        REPO / "dashboard/sidebar.py",
        REPO / "dashboard/components/ai_panel.py",
        REPO / "ai/option_selector.py",
        REPO / "ai/zero_to_hero.py",
        REPO / "services/ai_service.py",
        REPO / "services/market_service.py",
    ]
    result = subprocess.run(
        ["python", "-m", "py_compile", *map(str, targets)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        fail("Python compilation check failed.")
    print("Python compilation check: PASS")


def main() -> None:
    if not (REPO / ".git").exists():
        fail("Run this installer from the NPAT repository root, e.g. cd C:\\NPAT")

    backup_root = REPO / ".npat_patch_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root.mkdir(parents=True, exist_ok=True)

    changed = [
        REPO / "app.py",
        REPO / "dashboard/sidebar.py",
        REPO / "dashboard/components/ai_panel.py",
        REPO / "ai/option_selector.py",
        REPO / "services/ai_service.py",
        REPO / "services/market_service.py",
    ]
    for path in changed:
        backup(path, backup_root)

    for relative, source in OVERLAY.items():
        destination = REPO / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    patch_market_service()
    compile_check()

    print("\nNPAT Sprint-7 Index + Zero-to-Hero patch applied.")
    print(f"Backup: {backup_root}")
    print("Next: streamlit run app.py")
    print("No live Groww order placement was enabled.")


if __name__ == "__main__":
    main()
