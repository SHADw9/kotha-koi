#!/usr/bin/env bash
# Keep the Android WebView assets and the Tauri frontend in sync with web/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_ASSETS="$ROOT/android/app/src/main/assets"
DESKTOP_DIST="$ROOT/desktop/dist"

mkdir -p "$ANDROID_ASSETS" "$DESKTOP_DIST"

for file in index.html data.js diagrams.js; do
  cp "$ROOT/web/$file" "$ANDROID_ASSETS/$file"
  cp "$ROOT/web/$file" "$DESKTOP_DIST/$file"
done

echo "Synced web assets to android/app/src/main/assets and desktop/dist."
