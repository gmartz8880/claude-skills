---
name: ancient-script-translator
description: "Translates and transliterates ancient and historical writing from a photo or scan, covering Egyptian hieroglyphics, Mesopotamian cuneiform, Latin and Ancient Greek inscriptions, and European handwritten or printed texts from the last ~900 years (medieval and early-modern paleography, e.g. blackletter, secretary hand, Old/Middle English, Old French, old German scripts). Load this skill when the user uploads or shares an image of an inscription, stone tablet, cuneiform tablet, hieroglyphic carving, old manuscript, historical document, or antique handwriting and asks to read, transcribe, transliterate, translate, or decode it. Delivers the transliteration, an English translation, and scholarly/confidence notes as text directly in the chat."
metadata:
  author: user
  version: '1.0'
---

# Ancient Script Translator

## When to Use This Skill

Use this skill whenever the user provides (uploads, attaches, or links to) a photo or scan of writing and asks to read, transcribe, transliterate, translate, or decode it, and the writing falls into one of these categories:

- **Egyptian hieroglyphics** — carved or painted glyphs on stone, papyrus, jewelry, etc.
- **Cuneiform / Mesopotamian scripts** — wedge-shaped marks on clay tablets or stone (Sumerian, Akkadian, Babylonian, Assyrian, Old Persian, etc.)
- **Latin & Ancient Greek** — classical inscriptions, manuscripts, or printed text in these languages
- **European texts from the past ~900 years** — medieval and early-modern handwriting or print in European languages (Old/Middle English, Old French, Old German/Fraktur, blackletter, secretary hand, Church Latin, early Italian/Spanish, etc.)

If the user has not attached an image yet, ask them to provide one (a clear, well-lit photo works best; multiple angles or close-ups of a damaged/worn section help).

## Workflow

1. **View the image directly.** Use the `read` tool on the image file — vision-capable reading lets you see the actual glyphs, wedges, or letterforms rather than relying on a generic OCR pipeline (which is unreliable for these scripts). If there are multiple photos of the same object (e.g. different angles or lighting), read all of them — ancient surfaces are often worn, and a second angle can resolve an ambiguous sign.

2. **Identify the script and language.** State your identification (e.g. "Middle Egyptian hieroglyphics," "Old Babylonian cuneiform," "Ancient Greek uncial," "15th-century English secretary hand") and your confidence in it. If genuinely ambiguous between two scripts, briefly note the alternative rather than stopping to ask — proceed with your best read.

3. **Transcribe sign-by-sign or line-by-line.** Work systematically (right-to-left, left-to-right, or boustrophedon as appropriate for the script/period). Note the reading direction you used.

4. **Transliterate.** Convert the transcription into the standard scholarly transliteration convention for that script (see script-specific notes below). Flag any signs/letters you could not confidently identify with a bracketed note like `[uncertain: possibly ...]` or `[damaged]` rather than silently guessing.

5. **Translate into English.** Provide a fluent English translation. If a literal/word-for-word rendering would help the user understand the grammar, include it alongside the fluent translation.

6. **Verify against known sources when possible.** If the inscription matches or resembles a known, published text (e.g. a famous stele, a documented manuscript, a well-known Latin/Greek passage), use `search_web` or `search_vertical` (vertical="academic") to check your reading against published transliterations/translations, and cite what you find. Do not force a match — only cite a source if it genuinely corresponds.

7. **Give a confidence assessment.** Ancient scripts are frequently ambiguous, damaged, or debated among scholars. Always state plainly how confident you are overall (e.g. "high confidence," "several signs uncertain due to wear," "this is a best-effort scholarly reading, not a certified translation") — never present a shaky reading as definitive fact.

## Script-Specific Notes

### Egyptian Hieroglyphics
- Use the standard transliteration alphabet (e.g. ꜥ, ḏ, ḫ, š, ṯ, ẖ, etc.; a simplified ASCII fallback like "3" for ꜥ is acceptable if special characters render poorly).
- Note determinatives and phonetic complements separately from the core translation when they materially affect meaning.
- Watch for cartouches (royal names) — call these out explicitly since they're often the easiest and most reliable part of an inscription to identify.
- Note whether the text is Old, Middle, or Late Egyptian if identifiable, since grammar differs.

### Cuneiform / Mesopotamian Scripts
- Identify the underlying language (Sumerian, Akkadian, etc.) — the same wedge shapes can represent different languages/periods.
- Transliterate using the standard convention: Sumerian logograms in CAPITALS/small caps, Akkadian syllabic values in lowercase italics-equivalent (describe as italicized in plain text, e.g. *šarrum*), with hyphens between syllables.
- Note the tablet's likely genre if apparent (royal inscription, administrative record, letter, literary text) since this affects expected vocabulary.

### Latin & Ancient Greek
- Expand standard abbreviations and ligatures common in inscriptions and manuscripts (e.g. Latin "&" as "et", suspended endings, Greek nomina sacra) and note where you expanded something.
- For inscriptions, note any use of interpuncts (word-dividing dots) and unusual letterforms (e.g. archaic Greek letters, Latin epigraphic variants).
- Provide both the transliterated/normalized text and a fluent English translation.

### European Texts from the Past ~900 Years (Paleography)
- This category also covers older/extinct European scripts and languages that fall within the timeframe but predate or sit alongside classical Latin/Greek, such as Celtic inscriptions (Gaulish, Celtiberian, Ogham, Old Irish/Welsh/Breton) and other minor historical language monuments (e.g. Old Prussian) — see `references/README.md` for bundled background on these.
- Identify the script style if possible (e.g. Carolingian minuscule, blackletter/Gothic, Fraktur, secretary hand, italic hand, court hand) and approximate century — this materially affects letterform interpretation.
- Watch for scribal abbreviation marks (macrons over vowels, Tironian "et" ⁊, superscript letters) and expand them, noting the expansion.
- Identify the underlying language before translating (Old English, Middle English, Old French, Latin, early Modern German, etc.) since letterforms alone can be ambiguous between languages of the same period/region.
- For Old/Middle English or other older forms of modern languages, provide a modern-English translation rather than just modernized spelling.

## Output Format

Deliver the result as plain text directly in the chat (not as a file), organized like this:

```
## Script & Language
[Your identification and confidence]

## Transcription / Transliteration
[Sign-by-sign or line-by-line transliteration, with [uncertain]/[damaged] flags as needed]

## Translation
[Fluent English translation]
[Optional: literal/word-for-word gloss if helpful]

## Notes
[Confidence level, damaged/ambiguous sections, any scholarly sources checked with links, historical/cultural context worth mentioning]
```

## Reference Library

This skill includes a `references/` folder with supplementary scholarly sources on European historical languages and scripts (Early Modern English, old Celtic languages/scripts, 16th-century Italian vernacular pedagogy, Byzantine manuscript-art dating cues, Old Prussian written monuments, and Semitic-language historiography). Read `references/README.md` first to see what each file covers and when it's actually relevant, then read only the specific file (or section, via offset/limit) that applies to the current task. These are contextual/background aids, not decipherment keys — keep following the core Workflow above for the actual transcription and translation.

## Caveats

- Always be explicit that ancient-script translation is inherently interpretive — even professional epigraphers and papyrologists disagree on difficult passages. Never overstate certainty.
- If the image quality is too poor to make any confident reading (too blurry, too worn, too small), say so plainly and suggest what kind of photo (angle, lighting, close-up) would help, rather than fabricating a translation.
- Do not invent a translation for a script you cannot identify — say you're uncertain of the script itself if that's the case, and offer your best guess with caveats.

## Running This Skill in Claude

This skill was exported from Perplexity Computer. When a step names a tool Claude does not have, use the closest Claude equivalent:

- `search_web`, `search_vertical` (academic), `fetch_url` — use Claude's web search and web fetch.
- `browser_task` / `use_local_browser` — use Claude in Chrome if it is enabled; otherwise use web search and ask the user to paste content from login-only sites (such as the SRU library or JSTOR).
- `read` — open the file from the skill folder or the user's upload.
- `share_file` — save the finished file and provide it as a downloadable file.
- Other skills named here (for example `humanize-ai-text`, `sds-bible`, `office/pdf`) — use the matching uploaded skill if installed; otherwise follow the instructions directly with code execution (python-docx, openpyxl, reportlab).
- Workspace paths like `/home/user/workspace/...` — save output to Claude's normal output folder instead.
