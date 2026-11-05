---
name: sru-research
description: Deep academic research skill for finding credible sources on any topic. Load when the user says "research [topic]" or asks to find sources, gather evidence, or look up information for a paper. Searches Google Scholar first, then runs simultaneous multi-engine searches across Google, DuckDuckGo, JSTOR (via SRU library session), Ecosia, and Bing, with built-in academic search as a fallback. Fetches full article content for specific sources found. Delivers a structured written report AND an annotated source list. Always asks the user which citation style to use (MLA, APA, or Chicago) before delivering output.
---

# SRU Research Skill

## When to Use This Skill

Load this skill when the user says **"research [topic]"** or asks to:

- Find sources or evidence for a paper
- Look up information on a topic
- Gather credible academic or scholarly sources
- Research anything for an assignment

## Step-by-Step Workflow

### Step 1 — Ask for Citation Style

Before beginning any research, ask the user which citation style they want:

- MLA
- APA
- Chicago

Do not proceed until you have their answer.

### Step 2 — Google Scholar Search (Primary)

Use `search_vertical` with `vertical: "academic"` to search Google Scholar for peer-reviewed, scholarly sources on the topic. Run 2–3 targeted queries to maximize coverage. Collect all results including titles, authors, publication dates, and DOIs.

### Step 3 — JSTOR via SRU Library (Second Priority)

Immediately after Google Scholar, use `browser_task` with `use_local_browser: true` to search JSTOR through the user's Slippery Rock University library proxy session at `https://www.sru.edu/library`. Navigate to the JSTOR database link from the library portal, search for the topic, and extract any available full-text articles or abstracts including title, author(s), journal, date, and URL.

This step runs before the general web engines and uses the user's authenticated SRU library session to access full JSTOR content.

### Step 4 — Multi-Engine Simultaneous Search

Run ALL of the following searches **at the same time** (in parallel) using `search_web`:

1. **Google** — general credible sources, news, government (.gov), and educational (.edu) sites
2. **DuckDuckGo** — alternative results to avoid filter bubbles
3. **Bing** — additional indexed sources
4. **Ecosia** — supplemental web results

For `search_web`, use different but related query variations across engines to maximize unique results. Combine results and deduplicate.

### Step 5 — Academic Search Fallback

If fewer than 5 credible sources have been found after Steps 2 and 3, use the built-in `search_vertical` with `vertical: "academic"` again with broader or alternative query terms as a fallback.

### Step 6 — Full Article Fetching

For any source where a URL is available, use `fetch_url` to retrieve the full article content or abstract. Extract:

- Title
- Author(s)
- Publication / journal name
- Date
- Key findings or argument (2–4 sentences)
- URL or DOI

### Step 7 — Compile and Deliver Output

Deliver TWO things:

#### A. Written Research Report

A structured markdown report with:

- **Introduction** — overview of the topic and what the research covers
- **Key Findings** — organized by theme or subtopic, drawing on the sources found
- **Conclusion** — brief synthesis of what the sources collectively say
- Inline citations in the user's chosen citation style throughout

#### B. Annotated Source List

A numbered list of all credible sources found. Each entry includes:

- Full citation in the user's chosen style (MLA, APA, or Chicago)
- 2–3 sentence annotation explaining what the source covers and why it is credible/useful

### Step 7b — Name Verification Pass (MANDATORY)

Before the source quality check and final delivery, scan the entire research report and annotated source list — including any MLA/APA/Chicago header block, cover page, running header, footer, and Works Cited/References/Bibliography entries — for the string "Gary Martz".

- If "Gary Martz" appears anywhere in the output, replace every instance with "Gabriel Martz".
- Also check for near-variants ("Gary martz", "gary Martz", "GARY MARTZ") and normalize them all to "Gabriel Martz".
- The user's real name is Gabriel Martz. Never leave "Gary Martz" in any final output.
- This pass is mandatory and must run before delivery, regardless of citation style or output format.

### Step 8 — Source Quality Check

Before finalizing, evaluate each source for credibility using the SIFT method:
- **Stop** — don't accept the source at face value
- **Investigate the source** — check author credentials, publication reputation
- **Find better coverage** — cross-reference key claims
- **Trace claims** — verify claims go back to original research

Remove or flag any sources that appear unreliable, biased, or unverifiable.

## Output Format

Always deliver:
1. The written research report (in the chat or as a downloadable Word .docx if the user prefers)
2. The annotated source list

Ask the user if they want the output as a downloadable Word document or in-chat markdown.

## Preferred Formatting for Word Documents

When delivering research as a Word document, use the following defaults unless the user requests otherwise:

- **Font: Comfortaa** for all text (body, headings, title, works cited, annotations). This is the user's preferred font.
- Body text: 11pt, dark near-black (`#1F1F1F`), 1.25 line spacing, justified, block paragraphs (no first-line indent), 9pt space after.
- Section headings: uppercase, bold, teal accent color (`#01696F`), with a thin light-gray bottom rule (`#D4D1CA`).
- Title block: large bold title, italic muted subtitle, a small uppercase "RESEARCH REPORT" eyebrow above the title in accent teal, and a horizontal accent rule below the subtitle.
- Meta line under the title showing AUTHOR / COURSE / INSTRUCTOR / DATE with uppercase muted labels.
- Running header (report title in muted gray with a bottom rule) and footer ("Page X of Y" right-aligned in muted gray) on every page.
- Works Cited: hanging indent (0.5"), links in accent teal and underlined.
- Annotated Source List: hanging-indent citation followed by the annotation in italic muted gray.
- Page: US Letter, 1" margins.

Use the build script at `/home/user/workspace/build_docx_social_v2.js` as the reference template for structure and styling.

## Notes

- Always prioritize peer-reviewed and scholarly sources over general web sources
- Government (.gov) and university (.edu) sites are preferred for web sources
- Wikipedia may be used to find leads but should never be cited directly
- The SRU library JSTOR session requires the user's local browser — always use `use_local_browser: true` when accessing library resources

## Running This Skill in Claude

This skill was exported from Perplexity Computer. When a step names a tool Claude does not have, use the closest Claude equivalent:

- `search_web`, `search_vertical` (academic), `fetch_url` — use Claude's web search and web fetch.
- `browser_task` / `use_local_browser` — use Claude in Chrome if it is enabled; otherwise use web search and ask the user to paste content from login-only sites (such as the SRU library or JSTOR).
- `read` — open the file from the skill folder or the user's upload.
- `share_file` — save the finished file and provide it as a downloadable file.
- Other skills named here (for example `humanize-ai-text`, `sds-bible`, `office/pdf`) — use the matching uploaded skill if installed; otherwise follow the instructions directly with code execution (python-docx, openpyxl, reportlab).
- Workspace paths like `/home/user/workspace/...` — save output to Claude's normal output folder instead.
