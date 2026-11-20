#!/usr/bin/env python3
"""Build the vocabulary data used by the Words tab.

Sources
-------
* CEFR words          Oxford 3000/5000 CSV via github.com/nalgeon/words
* Academic phrases    Oxford Phrase List + OPAL via github.com/nalgeon/words
* IELTS AWL 570       github.com/shelfom/awl-570-flashcards (Simple Wiktionary)
* Bangla meanings     Nafisa41 100k JSON (GPL-3.0)
                      zakariahossen 13.5k dictionary (MIT) as fallback

Output: web/vocab.js
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
CACHE = Path("/tmp/opencode/vocab")
CACHE.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "oxford-5k.csv": "https://raw.githubusercontent.com/nalgeon/words/main/data/oxford-5k.csv",
    "oxford-phrase.csv": "https://raw.githubusercontent.com/nalgeon/words/main/data/oxford-phrase.csv",
    "oxford-opal.csv": "https://raw.githubusercontent.com/nalgeon/words/main/data/oxford-opal.csv",
    "awl.json": "https://raw.githubusercontent.com/shelfom/awl-570-flashcards/main/src/data/awl.json",
    "zakaria.json": "https://raw.githubusercontent.com/zakariahossen/English-Bangla-Dictionary/main/dictionary.json",
}

LEVEL_ORDER = {"a1": 1, "a2": 2, "b1": 3, "b2": 4, "c1": 5}

STOP = set(
    "a an the of to in for on with and or as at by from be is are was were that this these those "
    "it its not no more most such than which who whom what when where why how can could may might "
    "must should would do does did have has had will shall about into over under between through "
    "during without within across per via etc you we they he she me us them my your our their his "
    "her its see get make take give go come use used using one ones something anything thing things".split()
)


def fetch(name: str) -> Path:
    path = CACHE / name
    if not path.exists():
        print("downloading", SOURCES[name])
        with urllib.request.urlopen(SOURCES[name], timeout=120) as r:
            path.write_bytes(r.read())
    return path


def load_native_dictionary() -> dict[str, str]:
    text = (WEB / "dict.js").read_text(encoding="utf-8")
    rows = json.loads(text[text.index("[") : text.rindex("]") + 1])
    return {en.lower(): bn for en, bn in rows}


def load_zakaria() -> dict[str, str]:
    raw = json.loads(fetch("zakaria.json").read_text(encoding="utf-8"))
    return {k.lower(): ", ".join(v) for k, v in raw.items() if v}


def first_gloss(bn: str) -> str:
    """First clean sense: drop '(noun)' style tags and trailing notes."""
    part = re.split(r",\s*", bn)[0]
    part = re.sub(r"\s*\([^)]*\)\s*", " ", part).strip(" .;")
    return part


def make_lookup(native: dict[str, str], fallback: dict[str, str]):
    def lookup(word: str) -> tuple[str, bool]:
        key = word.strip().lower()
        for source in (native, fallback):
            bn = source.get(key)
            if bn:
                gloss = first_gloss(bn)
                if gloss:
                    return gloss, False
        return "", False

    return lookup


def phrase_gloss(phrase: str, lookup) -> tuple[str, bool]:
    gloss, _ = lookup(phrase)
    if gloss:
        return gloss, False
    words = [w for w in re.findall(r"[a-z][a-z'-]*", phrase.lower()) if w not in STOP]
    words.sort(key=len, reverse=True)
    for word in words:
        gloss, _ = lookup(word)
        if gloss:
            return gloss, True
    return "", False


def main() -> None:
    native = load_native_dictionary()
    zakaria = load_zakaria()
    lookup = make_lookup(native, zakaria)
    print(f"native {len(native):,} · fallback {len(zakaria):,}")

    # ---------------- CEFR words ----------------
    cefr: dict[str, dict] = {}
    with fetch("oxford-5k.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            word = (row.get("word") or "").strip()
            level = (row.get("level") or "").strip().lower()
            pos = (row.get("pos") or "").strip()
            if not word or not level:
                continue
            key = word.lower()
            cur = cefr.get(key)
            if cur is None:
                cefr[key] = {"word": word, "level": level, "pos": [pos] if pos else []}
            else:
                if LEVEL_ORDER.get(level, 9) < LEVEL_ORDER.get(cur["level"], 9):
                    cur["level"] = level
                if pos and pos not in cur["pos"]:
                    cur["pos"].append(pos)

    cefr_rows = []
    for item in cefr.values():
        gloss, _ = lookup(item["word"])
        derived = 0
        if not gloss:
            gloss, was_derived = phrase_gloss(item["word"], lookup)
            derived = 1 if was_derived else 0
        cefr_rows.append(
            [item["word"], item["level"], ", ".join(item["pos"]), gloss, derived]
        )
    cefr_rows.sort(key=lambda r: (LEVEL_ORDER.get(r[1], 9), r[0].lower()))

    # ---------------- IELTS AWL 570 ----------------
    awl_raw = json.loads(fetch("awl.json").read_text(encoding="utf-8"))["entries"]
    awl_rows = []
    for item in awl_raw:
        word = (item.get("word") or "").strip()
        if not word:
            continue
        gloss, _ = lookup(word)
        definition = re.sub(r"\s+", " ", (item.get("definition") or "")).strip()
        # Example sentences in the upstream set are CC BY-NC; only the
        # CC BY-SA Wiktionary definition is reused here.
        awl_rows.append(
            [word, int(item.get("sublist") or 0), (item.get("partOfSpeech") or "").strip(), gloss, definition, ""]
        )
    awl_rows.sort(key=lambda r: (r[1], r[0].lower()))

    # ---------------- phrases ----------------
    phrases = []
    seen = set()

    def add_phrase(text: str, level: str, kind: str):
        text = re.sub(r"\s+", " ", text).strip()
        key = text.lower()
        if not text or key in seen:
            return
        seen.add(key)
        gloss, derived = phrase_gloss(text, lookup)
        # Word-by-word guesses are too unreliable for idioms ("a lot" → lottery),
        # so only keep exact phrase matches.
        if derived:
            gloss = ""
        phrases.append([text, level, gloss, kind, 0])

    with fetch("oxford-phrase.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            add_phrase(row.get("word") or "", (row.get("level") or "").upper(), "phrase")
    with fetch("oxford-opal.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            add_phrase(row.get("word") or "", "", "academic")

    # Glossed phrases first: they are the most useful while browsing.
    phrases.sort(key=lambda r: (0 if r[2] else 1, 0 if r[3] == "phrase" else 1,
                                LEVEL_ORDER.get(r[1].lower(), 9), r[0].lower()))

    payload = {
        "cefr": cefr_rows,
        "awl": awl_rows,
        "phrases": phrases,
        "meta": {
            "cefr": len(cefr_rows),
            "awl": len(awl_rows),
            "phrases": len(phrases),
            "levels": ["A1", "A2", "B1", "B2", "C1"],
        },
    }

    out = (
        "/* kotha-koi vocabulary — generated by scripts/build-vocab.py.\n"
        "   CEFR: Oxford 3000/5000 · IELTS: AWL 570 · phrases: Oxford/OPAL.\n"
        "   Bangla glosses: Nafisa41 (GPL-3.0) + zakariahossen (MIT).\n"
        "   See VOCAB-LICENSE.md for sources and terms. */\n"
        "window.KK_VOCAB=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    )
    (WEB / "vocab.js").write_text(out, encoding="utf-8")
    print(
        f"wrote web/vocab.js: {len(out)/1024:.0f} KB · "
        f"{len(cefr_rows):,} CEFR · {len(awl_rows)} AWL · {len(phrases):,} phrases"
    )
    with_gloss = sum(1 for r in cefr_rows if r[3]) + sum(1 for r in awl_rows if r[3])
    print(f"Bangla gloss coverage: {with_gloss:,} / {len(cefr_rows)+len(awl_rows):,} core entries")


if __name__ == "__main__":
    main()
