#!/usr/bin/env python3
"""Keep the Android WebView assets and the Tauri frontend in sync with web/."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ("index.html", "data.js", "diagrams.js", "dict.js", "vocab.js", "verbs.js")
TARGETS = (
    ROOT / "android" / "app" / "src" / "main" / "assets",
    ROOT / "desktop" / "dist",
)

for target in TARGETS:
    target.mkdir(parents=True, exist_ok=True)
    for name in SOURCES:
        shutil.copy2(ROOT / "web" / name, target / name)

print("Synced web assets to android/app/src/main/assets and desktop/dist.")
