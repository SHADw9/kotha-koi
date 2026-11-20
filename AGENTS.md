# AGENTS.md

kotha-koi is an offline English-learning app (A1–C2, Bengali/English UI). One
plain HTML/CSS/JS UI is shared by three targets: Android WebView, Tauri desktop,
and a static web build. No server, accounts, or network calls; all state is in
`localStorage`.

## Source of truth and generated copies

- `web/` is the only UI source. `web/index.html` contains all markup, CSS and app
  JS inline (~2,500 lines, vanilla JS, no bundler). Data lives in `web/data.js`,
  `web/diagrams.js`, `web/dict.js`, `web/vocab.js`.
- **Never edit** `android/app/src/main/assets/` or `desktop/dist/` — they are
  generated copies of `web/`.
- After any `web/` change, run `python3 scripts/sync-web.py` to copy all five
  assets to Android and desktop.
- `scripts/sync-web.sh` is stale (omits `dict.js` and `vocab.js`). Use the
  `.py` version; CI does too.
- `desktop/src-tauri/` is a thin Tauri 2 shell with `frontendDist: "../dist"`.
  Android's `MainActivity.kt` is a WebView shell exposing native TTS, ads and
  file saving through the `AndroidBridge` JavaScript interface.

## Commands

```bash
# Web preview
cd web && python3 -m http.server 8080

# Sync shared assets after editing web/
python3 scripts/sync-web.py

# Android (JDK 17, Android SDK platform 35, build-tools 35.0.0)
cd android && ./gradlew assembleRelease
# Version overrides: -PappVersionName=1.2.3 -PappVersionCode=42

# Desktop (needs Rust + Tauri CLI; Linux deps are in .github/workflows/release.yml)
cd desktop && cargo tauri build

# Regenerate data (only when the upstream datasets change)
python3 scripts/build-dict.py    # writes web/dict.js, downloads source or accepts a local JSON path
python3 scripts/build-vocab.py   # writes web/vocab.js from data/word-bank-v3.json
python3 scripts/build-vocab.py --legacy  # old upstream rebuild; needs web/dict.js + network cache
```

There is **no test suite, linter, formatter, typecheck, or package manager** in
this repo. Verify manually by serving `web/` and exercising the affected tab;
after syncing, compare copies with `cmp`.

## Editing data

- `web/data.js` is a 2.2 MB single-line `window.STUDY_DATA = {...}` payload.
  Do not hand-edit or reformat it. Parse and rewrite it with Python + `json`,
  preserving the wrapper and compact encoding.
- Content is bilingual. Units use Bengali base fields (`title`, `explain`,
  `notes`, …) plus `*_en` variants; questions have `explain` + `explain_en`;
  chapters and sentence categories have `title_en`/`sub_en`; conversations and
  examples use `bn`/`en` pairs. UI helpers `T(bn,en)` and `LG(obj,field)` select
  by the `bp_lang` setting. New learner-facing content needs both languages or
  English mode shows blanks.
- `web/dict.js` (~7 MB) and `web/vocab.js` are generated single-line files.
  Never edit or reformat them; change `scripts/build-*.py` instead. `vocab.js`
  is compiled from `data/word-bank-v3.json` (schema v2-meanings). They are
  loaded lazily by injecting a `<script>` when the Dictionary/Words tab opens —
  do not add static script tags for them.
- `web/data.js` has no generator script; it is curated content (see licenses
  below).

## Platform / app quirks

- Keep everything offline-capable: no CDNs, external fonts, analytics, or
  frameworks.
- Native features are optional enhancements behind `AndroidBridge`: TTS
  (`speak`, `stopSpeak`, `canSpeak`), ads (`showInterstitial`,
  `showRewarded`), and `saveFile`. Preserve the web fallbacks
  (`speechSynthesis`, Blob download) so desktop/web still work.
- Ads run only on Android. Ad unit IDs in `MainActivity.kt` and
  `AndroidManifest.xml` are Google **test** IDs; do not swap in live IDs unless
  asked.
- Persistence keys are a compatibility contract: `study_center_progress_v1`,
  `kk_theme`, `bp_lang`, `kk_dict_recent`, `kk_vocab_known`. Don't break or
  rename them casually.
- Themes are selected by `data-theme` on `<html>` before first paint; styling
  uses CSS variables. Keep both Bengali and English UI copy in sync.

## Release and licensing gotchas

- Pushing to `main` triggers `.github/workflows/release.yml`, which creates a
  GitHub release, builds Android/desktop/web bundles, and tags
  `v1.0.<run-number>`. Do not push to `main` just to test changes; a `v*` tag
  sets an explicit version.
- The release keystore and passwords are **intentionally committed**
  (`android/kotha-koi-release.keystore`, `android/release-signing.properties`) so
  CI can sign updates. Don't remove or "secure" them; CI secrets override via a
  gitignored `android/keystore.properties`.
- License split: app code is MIT (`LICENSE-CODE`), lesson/practice content is
  All Rights Reserved (`CONTENT-LICENSE.md`), dictionary data is GPL-3.0
  (`DICTIONARY-LICENSE`), and the word bank has mixed terms
  (`VOCAB-LICENSE.md`). Don't relocate content or strip license notices.
