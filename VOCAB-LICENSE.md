Vocabulary data — sources and terms
====================================

`web/vocab.js` is a compilation. Each part keeps the terms of its source;
the MIT license of the application code does not override them.

1. CEFR words, Oxford Phrase List, OPAL
---------------------------------------
Source: https://github.com/nalgeon/words
  - `oxford-5k.csv`    Oxford 3000 and 5000, with CEFR levels
  - `oxford-phrase.csv` Oxford Phrase List
  - `oxford-opal.csv`  Oxford Phrasal Academic Lexicon

The lists are published by Oxford University Press through Oxford Learner's
Dictionaries (https://www.oxfordlearnersdictionaries.com/wordlists/).
The CSV mirror above has no separate license. kotha-koi includes the lists as a
study index and does not relicense them; Oxford's own terms apply. If you fork
this project for commercial distribution, review those terms first.

2. IELTS Academic Word List (AWL 570)
-------------------------------------
Headwords: Coxhead, A. (2000). A New Academic Word List. TESOL Quarterly, 34(2),
213–238. The 570 headwords are widely reproduced for teaching.

Definitions and sublist data:
https://github.com/shelfom/awl-570-flashcards
  - repository code: MIT
  - definitions adapted from Simple English Wiktionary, CC BY-SA 4.0
    (https://creativecommons.org/licenses/by-sa/4.0/)
  - the upstream example sentences are CC BY-NC 4.0 and are **not** included
    in kotha-koi

The AWL definitions in `vocab.js` are therefore distributed under CC BY-SA 4.0.

3. Bangla glosses
-----------------
The Bangla meanings are joined from the same two sources as the dictionary:

  - Nafisa41, Dictionary--English-to-Bangla (GPL-3.0) — see DICTIONARY-LICENSE
  - Md Zakaria Hossen, English-Bangla-Dictionary (MIT)
    https://github.com/zakariahossen/English-Bangla-Dictionary

Words that have no entry in either source are shown with “—” and no gloss.

4. Phrases
----------
Phrase entries carry a Bangla gloss only when the exact phrase exists in one of
the dictionaries. Word-by-word guesses are deliberately not generated, because
they are often wrong for idioms.

5. Machine-assisted senses
--------------------------
`data/word-bank-v3.json` adds extra senses to some CEFR and AWL entries. These
draft Bengali senses and English glosses were produced with
`gemini-3.5-flash-lite` and are marked `"reviewed": false` in the source file.
They are study aids rather than authoritative dictionary definitions; review
them before commercial redistribution. The primary senses, the Oxford word and
phrase lists, and the AWL definitions keep the sources and terms described
above.

Attribution in the app
----------------------
The Words tab links to Oxford Learner's Dictionaries, the AWL, Nafisa41 and
zakariahossen. Please keep those links if you reuse this data.
