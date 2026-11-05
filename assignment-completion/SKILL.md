---
name: assignment-completion
description: Completes academic assignments from start to finish for the user. Load this skill when the user shares an assignment prompt, rubric, or instructions and asks you to complete, write, do, finish, or work on it. Handles any assignment type including essays, research papers, discussion posts, lab reports, case studies, reflections, and short answer questions. Automatically detects required citation style (MLA, APA, Chicago) from the assignment instructions. Always runs the humanize-ai-text user skill at the end to rewrite the completed assignment so it sounds natural and passes AI detection tools. Asks the user for their preferred output format before delivering.
metadata:
  author: gmartz2006
  version: '2.0'
---

# Assignment Completion

## When to Use This Skill

Load this skill when the user:

- Pastes or describes an assignment prompt, rubric, or set of instructions
- Says things like "do this assignment", "write this for me", "complete this", "help me finish this", "work on this", or "do my homework"
- Shares a due date, point value, or grading rubric alongside a writing task
- Uploads a file (PDF, DOCX, image) containing assignment instructions

## Step-by-Step Instructions

### Step 1 — Parse the Assignment

Read the full assignment prompt carefully. Extract and note:

- **Assignment type**: essay, research paper, discussion post, lab report, case study, reflection, short answer, presentation, spreadsheet/data table, etc.
- **Topic or subject**: what the assignment is about
- **Required length**: word count, page count, number of paragraphs, number of slides, etc.
- **Citation style**: look for explicit mentions of MLA, APA, or Chicago. If not stated, infer from context (humanities → MLA, social sciences/safety → APA, history → Chicago). If truly ambiguous, default to MLA.
- **Due date and point value**: note these but do not let them affect content quality
- **Special requirements**: specific sources required, particular sections, formatting rules, rubric criteria

**Detect the required file format** from the assignment instructions:

- If the assignment mentions slides, a presentation, PowerPoint, or a slideshow → produce a **PowerPoint (.pptx)**
- If the assignment mentions a spreadsheet, data table, chart, Excel, or data analysis → produce an **Excel spreadsheet (.xlsx)**
- If the assignment mentions an essay, paper, report, post, reflection, or written response → produce a **Word document (.docx)**
- If the format is ambiguous, default to **Word (.docx)**

Note the detected format and carry it through the entire workflow. The humanizing and quality check steps apply to text-based content only — for PowerPoint, humanize the slide text; for Excel, focus on accuracy and clarity of data/content rather than humanizing.

### Step 2 — Research (if needed)

For assignments requiring factual information, outside sources, or evidence, use the following sources in order of preference:

1. **Google Scholar (primary)**: Use `browser_task` with `use_local_browser: true` to search [scholar.google.com](https://scholar.google.com) for peer-reviewed articles, books, and academic papers. Extract titles, authors, publication years, journal names, and links to full text when available. This should be the first and main source for academic research.

2. **Multi-engine web search**: Search across the following engines using `browser_task` with `use_local_browser: true`. Run all simultaneously and deduplicate overlapping results:
   - **Google**: [google.com](https://www.google.com)
   - **DuckDuckGo**: [duckduckgo.com](https://www.duckduckgo.com)
   - **JSTOR via SRU Library**: [jstor.org](https://www.jstor.org) — access through the user's Slippery Rock University library session. Before opening, notify the user: "Opening JSTOR using your SRU library session — you may need to log in if you aren't already."
   - **Ecosia**: [ecosia.org](https://www.ecosia.org)
   - **Bing**: [bing.com](https://www.bing.com)
   Search the same topic query on each. Collect unique, credible results (peer-reviewed articles, .gov, .edu, reputable publications) and deduplicate any overlapping sources.

3. **Built-in academic search**: Use `search_vertical` with `vertical: academic` as a fallback if the above sources do not yield sufficient results.

4. **Full article fetching**: Use `fetch_url` to read the full content of any specific article or source URL found.

- Collect at least 2–3 credible sources unless the assignment specifies otherwise
- Note all source details (author, title, publication, URL, date) for citations

For assignments based on course material or personal reflection, skip research and proceed directly to writing.

### Step 3 — Write the Assignment

Write the complete assignment from scratch following academic conventions:

- Match the appropriate **academic tone and grade level** for a university student at Slippery Rock University
- Follow the **assignment type structure**:
  - Essays/research papers: introduction with thesis, body paragraphs, conclusion
  - Discussion posts: direct answer, supporting evidence, personal connection or question
  - Lab reports: abstract, introduction, methods, results, discussion, conclusion
  - Case studies: background, analysis, recommendations
  - Reflections: personal voice, connection to course concepts
- Meet or slightly exceed the required length
- Integrate sources naturally with proper **in-text citations** in the detected citation style
- Build a **Works Cited / References / Bibliography** page in the correct format

### Step 4 — Confirm Works Cited and Citation Style

Before humanizing, ask the user the following two questions in order:

**Question 1:**
> "Would you like a Works Cited / References page included at the end of the assignment?"

- If **yes**: proceed to Question 2
- If **no**: skip the Works Cited page entirely and proceed to writing

**Question 2** (only if yes to Question 1):
> "What citation style would you like for the Works Cited page — MLA, APA, or Chicago?"

- Apply the chosen citation style to all in-text citations and the Works Cited / References / Bibliography page
- If the user already specified a citation style in the assignment prompt, pre-fill this but still confirm with the user

### Step 6 — Humanize the Text (Five Passes)

This is the final processing step before delivery. Load and apply the **humanize-ai-text** user skill using the following sequence — all five passes are mandatory and none may be skipped:

**Parallel passes (first three — run simultaneously):**
- Run the humanize-ai-text skill on the completed assignment text three times at the same time, in parallel
- Each of the three passes independently rewrites the text to sound natural and human-written, targeting AI detection tools (Turnitin, GPTZero, ZeroGPT)
- Once all three parallel passes are complete, compare the outputs and select the best one — the version that reads most naturally and least like AI
- Save the selected output as the working text

**Sequential passes (fourth and fifth — run one after the other):**
- **Fourth pass**: Run the working text from the parallel phase through the humanize-ai-text skill again
- Save the output from the fourth pass
- **Fifth pass**: Take the output from the fourth pass and run it through the humanize-ai-text skill one final time
- The output of the fifth pass is the final completed assignment text

All five passes are mandatory. The parallel phase maximizes variation and selects the strongest rewrite; the sequential phase then refines it further for maximum naturalness and AI detection evasion.

### Step 7 — Name Verification Pass (MANDATORY)

Before confirming the output format, scan the entire assignment text — including any MLA/APA/Chicago header block, cover page, running header, footer, and Works Cited/References/Bibliography entries — for the string "Gary Martz".

- If "Gary Martz" appears anywhere in the document, replace every instance with "Gabriel Martz".
- Also check for near-variants ("Gary martz", "gary Martz", "GARY MARTZ") and normalize them all to "Gabriel Martz".
- The user's real name is Gabriel Martz. Never leave "Gary Martz" in any final output.
- This pass is mandatory and must run after humanization and before delivery.

### Step 8 — Confirm Output Format

After all quality checks are complete, ask the user for their preferred format based on the detected file type from Step 1:

**If the detected format is Word (.docx):**
> "How would you like the final assignment delivered — as a Word document (.docx), PDF, or plain text?"
- **Word (.docx)**: deliver the file directly
- **PDF**: convert the final DOCX to PDF using available tools
- **Plain text**: paste the final text directly in the chat

**If the detected format is PowerPoint (.pptx):**
> "How would you like the final presentation delivered — as a PowerPoint (.pptx) or PDF?"
- **PowerPoint (.pptx)**: deliver the file directly
- **PDF**: export the presentation as a PDF using available tools

**If the detected format is Excel (.xlsx):**
> "How would you like the final spreadsheet delivered — as an Excel file (.xlsx) or PDF?"
- **Excel (.xlsx)**: deliver the file directly
- **PDF**: export the spreadsheet as a PDF using available tools

### Step 9 — Deliver

Share the final file using `share_file`. Include a brief summary of:

- What was written
- Citation style used
- Word/page count
- Any sources cited

## Important Notes

- Always complete the full assignment — never give an outline or partial draft unless the user explicitly asks for one
- Never ask the user to do any part of the writing themselves
- If the assignment prompt is unclear or missing key details (like length or topic), make a reasonable assumption and note it, rather than asking and stalling
- Keep the writing at a college undergraduate level — clear, well-organized, and academically sound
- Do not add disclaimers, caveats, or notes about AI generation in the final output
- The humanize-ai-text step is mandatory — never skip it

## Example Trigger Prompts

- "Here's my assignment, can you do it for me?"
- "Complete this essay prompt: [prompt]"
- "Do this discussion post for my political science class"
- "Write a 3-page paper on the 4th Amendment"
- "I have a case study due, here are the instructions"

## Running This Skill in Claude

This skill was exported from Perplexity Computer. When a step names a tool Claude does not have, use the closest Claude equivalent:

- `search_web`, `search_vertical` (academic), `fetch_url` — use Claude's web search and web fetch.
- `browser_task` / `use_local_browser` — use Claude in Chrome if it is enabled; otherwise use web search and ask the user to paste content from login-only sites (such as the SRU library or JSTOR).
- `read` — open the file from the skill folder or the user's upload.
- `share_file` — save the finished file and provide it as a downloadable file.
- Other skills named here (for example `humanize-ai-text`, `sds-bible`, `office/pdf`) — use the matching uploaded skill if installed; otherwise follow the instructions directly with code execution (python-docx, openpyxl, reportlab).
- Workspace paths like `/home/user/workspace/...` — save output to Claude's normal output folder instead.
