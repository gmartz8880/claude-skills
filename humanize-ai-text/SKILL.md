---
name: humanize-ai-text
description: Rewrites AI-generated text to sound natural and human-written, targeting both a genuine human tone and the ability to pass AI detection tools like Turnitin, GPTZero, and ZeroGPT. Load this skill when the user asks to humanize, rewrite, de-AI, make text sound human, bypass AI detection, or make writing less robotic. Always delivers output as a downloadable Word (.docx) document. Handles academic writing with support for MLA, APA, and Chicago citation styles. Writing level is flexible and adjusts to match the context of the provided text.
metadata:
  author: gmartz2006
  version: '1.0'
---

# Humanize AI Text Skill

## When to Use This Skill

Load this skill when the user asks to:

- Humanize AI-generated text
- Make writing sound more natural or less robotic
- Bypass or pass AI detection tools (Turnitin, GPTZero, ZeroGPT, Originality.ai, etc.)
- Rewrite AI text for academic assignments
- De-AI a draft or essay

## Instructions

### Step 0 — Ask for the User's Details (always first)

Before doing anything else, ask the user in one message:

- Their full name as it should appear in any header or byline (or "no name")
- Optional: a short sample of their own writing (a paragraph or two), so the rewrite sounds like them

If a profile skill, memory, or an earlier message in this conversation already gives any of these, show what you found and ask the user to confirm it instead of asking again. Never guess, and never use the skill author's name or school. Do not start the task until the user has answered.

### Step 1 — Receive the Text

Ask the user to paste the AI-generated text they want humanized if they haven't already.

### Step 2 — Detect Formatting & Citations

Before rewriting, scan the provided text for:

**Formatting (e.g., double spacing, specific fonts, headers):**
- If the user mentions or the text contains formatting instructions, ask: "Would you like me to preserve the formatting (e.g., double spacing, headers)?"
  - If yes, replicate those formatting rules in the Word document output.
  - If no, apply clean default formatting (Times New Roman, 12pt, 1-inch margins).

**Citations:**
- If the text contains any citations, footnotes, endnotes, or a works cited / references / bibliography section, ask: "What citation style should I use? (MLA, APA, Chicago, or another standard?)"
  - Format all citations in the output document according to the user's chosen style.
  - Do NOT alter citation content — only reformat style as needed.
  - Preserve all in-text citations exactly as provided.

### Step 3 — Humanize the Text

Rewrite the text using the following principles:

**Tone & Voice:**
- Write as a real student or person would — natural, slightly imperfect sentence variety
- Mix short punchy sentences with longer ones to break predictable AI rhythm
- Use contractions where appropriate (e.g., "it's", "didn't", "they're")
- Avoid overly formal, stiff, or textbook-like phrasing
- Remove filler phrases common in AI writing: "It is important to note that", "In conclusion, it is evident that", "Furthermore", "Moreover", "It is worth mentioning"

**Writing Level:**
- Adjust the complexity and vocabulary to match the context of the text provided
- Academic assignments: match the appropriate grade or course level (e.g., high school vs. college)
- Casual writing: keep it conversational and approachable

**Structure:**
- Vary paragraph and sentence lengths
- Do not start every paragraph with a topic sentence in the same predictable format
- Use transitional phrases that feel natural, not formulaic

**AI Detection Evasion (General):**
- Rephrase any highly predictable or templated sentence constructions
- Introduce slight stylistic quirks a real writer might use (rhetorical questions, brief asides, direct address where appropriate)
- Avoid overly balanced or symmetrical paragraph structures typical of AI
- Do not use bullet points or numbered lists unless they were in the original

**Turnitin-Specific Evasion:**
Turnitin analyzes deep writing patterns beyond word choice. Apply these additional techniques:
- **Break syntactic predictability**: Turnitin flags consistent subject-verb-object sentence patterns. Vary by occasionally starting sentences with clauses, prepositional phrases, or dependent fragments
- **Inject personal perspective**: Add brief first-person observations or hedged opinions where appropriate (e.g., "It seems like...", "What's interesting here is...") — Turnitin's model scores lower on opinionated, hedged language
- **Avoid parallel list structures**: Strings of parallel phrases ("X is..., Y is..., Z is...") are highly flagged — break them up or restructure as prose
- **Use informal connectors sparingly**: Words like "also", "but", "so", and "still" used mid-sentence or at the start signal human writing patterns
- **Introduce controlled imperfection**: Slightly informal word choices, a mild colloquialism, or an intentional sentence fragment (used sparingly) lower perplexity scores that Turnitin relies on
- **Avoid over-explanation**: AI text tends to over-explain every point. Cut redundant elaboration — humans assume context
- **Vary paragraph length intentionally**: One very short paragraph (1-2 sentences) among longer ones is a strong human signal
- **Do not use transitional summary sentences**: Phrases like "In summary, this section has shown..." or "As discussed above..." are heavily flagged — remove them entirely

**Punctuation & Symbol Removal (AI Detection Evasion):**
AI-generated text is strongly associated with certain punctuation patterns. Prefer full sentence restructuring to eliminate them; fall back to a safe substitution only when restructuring would change the meaning.
- **Em-dashes ( — or -- )**: Restructure the sentence to fold the em-dashed clause into the surrounding prose using a conjunction ("and," "but," "because," "which") or split it into two separate sentences. If restructuring changes the meaning, replace with a comma instead.
- **Semicolons ( ; )**: Always split into two separate sentences. Never substitute a comma for a semicolon — rewrite so both halves stand independently.
- **Colons ( : )**: Restructure to eliminate the colon entirely. If the colon introduces a list, convert the list into flowing prose. If it introduces a single clause, rewrite as a full sentence using "because," "which is," or a similar connector. Only keep a colon if it appears inside a direct quotation or citation that must not be altered.
- **Oxford (serial) commas in lists of three or more**: Rewrite the list as prose wherever possible (e.g., "X, Y, and Z" becomes "X and Y, as well as Z" or is folded into a sentence). If a list must remain, drop the Oxford comma and use a plain conjunction ("X, Y and Z").
- **Special symbols (§ silcrow, † dagger, ‡ double dagger, ¶ pilcrow, © ©, ™, ® and similar)**: Spell out the meaning in plain language (e.g., "§ 4" becomes "Section 4"; "©" becomes "copyright"). Never leave these symbols in the output unless they appear inside a direct quotation or a citation element that must not be altered.
- **After removing or replacing any of the above**, re-read the surrounding sentences to confirm the meaning is fully preserved and the prose flows naturally.

### Step 3b — Apply the User's Personal Writing Style

If the user gave a writing sample in Step 0, study it and match its sentence length, word choice, punctuation habits, and tone, and use that instead of the default profile below. If they gave no sample, apply the default profile below (it came from the skill author's writing). This ensures the output sounds like it was written by this specific person, not just a generic human.

**Sentence Structure:**
- Use long-to-medium sentences averaging 25–45 words, chaining clauses with "and," "but," and "because"
- Almost always begin sentences with a subject (name, pronoun, or noun phrase)
- Use occasional short punchy sentences to mark a strong opinion
- Avoid sentence fragments entirely
- Allow natural run-ons where multiple clauses are chained — do not over-correct these
- Use "However" and "Although" as the primary transitional openers

**Vocabulary:**
- Keep vocabulary plain and accessible — no literary or elevated diction
- Use these recurring verbs naturally where they fit: aligns, backs, reflects, supports, opposes, believes, argues, focuses
- Use "good intentions," "benefit(s)," "constituents," "stance(s)," and "as a whole" where appropriate
- Avoid metaphors, similes, figurative language, intensifiers ("absolutely," "incredibly"), and sensory descriptions entirely
- Political or domain-specific terms are acceptable when contextually appropriate

**Tone:**
- Factual/descriptive sections: neutral, third-person, formal-adjacent — no first person
- Opinion sections: earnest, direct, mildly blunt — shift to first person
- Avoid contractions in descriptive sections; allow near-colloquial phrasing in opinion sections
- Always ground opinions in stated reasoning immediately after the claim
- Do not hedge strong opinions — state them plainly. Reserve hedging for genuine nuance ("my opinion is mixed," "I partially disagree")

**Agreement and Disagreement:**
- Use these exact phrase patterns:
  - Agreement: "I agree with [X] because [reason]" / "I do agree with [X] because [reason]"
  - Disagreement: "I do not agree with [X] because [reason]" / "I disagree with [X] because [reason]"
  - Partial disagreement: "I partially disagree with [X] because yes, [concession], but [main point]"
  - Skepticism: "I am skeptical about [X] because [reason]"
- Always attach "because" directly to every opinion statement

**Paragraph Structure:**
- Open paragraphs with a plain factual or contextual statement
- Close opinion sections with a conditional qualifier that softens the verdict
- Do not use "In conclusion," "Therefore," "Furthermore," or "Moreover" as transitions
- Do not recap or summarize within a paragraph — move forward only

**First Person:**
- Use "I" only in opinion sentences — never in purely factual or descriptive sentences
- Standard first-person phrases: "I agree with," "I believe that," "I do not agree with," "I would," "I am skeptical about," "my opinion is mixed"

**Things to Avoid:**
- Bullet points or numbered lists (unless they were in the original)
- Rhetorical questions
- Passive voice
- Semicolons, em-dashes, colons (outside citations/quotes), Oxford commas, parentheses, exclamation points, and special symbols (§, †, ‡, ¶, ©, ™, ®)
- Academic hedges like "it could be argued," "one might suggest," "it is worth noting"
- Paragraph-ending summary sentences that recap what was just said
- Sarcasm or irony

**Punctuation:**
- Do NOT use serial (Oxford) commas in lists — use a plain conjunction without a preceding comma ("X, Y and Z")
- Place commas before "but," "however," and "because" mid-sentence
- Use quotation marks when importing another person's characterizing language or direct quotes
- Do not use semicolons under any circumstances
- Do not use em-dashes or colons outside of direct quotations or citation elements

### Step 3c — Name Verification Pass (MANDATORY)

Before generating the Word document, scan the fully humanized text — including any MLA/APA/Chicago header block, cover page, running header, footer, and Works Cited/References/Bibliography entries — for the user's name.

- Use the name the user gave in Step 0, spelled exactly as they gave it.
- If any author line, header, or byline shows a different or misspelled version of that name, replace it with the user's name.
- If the user did not want a name on the document, leave name lines out instead of inventing one.
- Never insert a name the user did not give you.
- This pass is mandatory and must run after humanization and before the .docx is built.

### Step 4 — Generate the Word Document

After rewriting, produce a downloadable .docx file using Python with the `python-docx` library. Follow this exact process:

1. Install the library if needed:
   ```bash
   pip install python-docx
   ```

2. Build the document with:
   - Font: Times New Roman, 12pt (default unless user requested otherwise)
   - Margins: 1 inch on all sides
   - Line spacing: Double (unless user requested otherwise or chose not to preserve formatting)
   - Paragraph spacing: 0pt before and after each paragraph
   - Page size: Letter (8.5 x 11 inches)
   - Apply the user's chosen citation style formatting to any citations section

3. Save the file to `/home/user/workspace/humanized_output.docx`

4. Share the file with the user using `share_file`.

### Step 5 — Confirm Delivery

After sharing the file, briefly tell the user:
- That the humanized version is ready
- Any key changes made (e.g., "Simplified sentence structures, removed AI filler phrases, preserved MLA citations")
- Remind them they can paste it back for another round if needed

## Key Rules

- ALWAYS output a Word (.docx) document — never paste the full rewritten text in chat only
- ALWAYS ask about citation style if citations are present
- ALWAYS ask about formatting preservation if the user mentions or the text contains formatting instructions
- NEVER alter citation content — only reformat style
- NEVER add new information or claims not present in the original text
- Keep the meaning and arguments of the original text fully intact

## Running This Skill in Claude

This skill was exported from Perplexity Computer. When a step names a tool Claude does not have, use the closest Claude equivalent:

- `search_web`, `search_vertical` (academic), `fetch_url` — use Claude's web search and web fetch.
- `browser_task` / `use_local_browser` — use Claude in Chrome if it is enabled; otherwise use web search and ask the user to paste content from login-only sites (such as a school library or JSTOR).
- `read` — open the file from the skill folder or the user's upload.
- `share_file` — save the finished file and provide it as a downloadable file.
- Other skills named here (for example `humanize-ai-text`, `sds-bible`, `office/pdf`) — use the matching uploaded skill if installed; otherwise follow the instructions directly with code execution (python-docx, openpyxl, reportlab).
- Workspace paths like `/home/user/workspace/...` — save output to Claude's normal output folder instead.
