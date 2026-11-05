# Intake (one round)

Ask with the question tool; skip anything already answered; always allow "you pick".

## Card 1 - multiple choice
1. **Where will the skill run?** All Claude surfaces (default) / Claude apps only (Claude.ai, Desktop, Cowork) /
   Claude Code only (allows extra fields: allowed-tools, $ARGUMENTS, hooks, context: fork)
2. **How autonomous?** Full (default: asks once, then does everything except the always-ask list) /
   Checkpoints (shows the plan before big steps) / Advisor (explains, user does the steps)
3. **Output format?** Files (Word, Excel, PDF, PowerPoint, code, zip) / Chat answer / Both / You pick
4. **Does it need anything installed or connected?** None / Python packages / Desktop apps
   (it may open them) / Online accounts or APIs (connectors or keys) / Not sure

## Card 2 - free text
5. **The job:** what should be finished when the skill is done? One concrete example request + result.
6. **Triggers:** words/phrases the user will say ("make an SDS", "build my calculator app").
7. **Inputs:** what the user provides (files, links, topics, numbers) and what the skill must ask for each time.
8. **Rules:** must-do / must-never items, style, sources to prefer or avoid, length, citation style.

## Converting an existing skill or prompt
Read every file first. Keep the user's intent and wording; change only format, portability, and gaps.
Map platform-specific tool names to neutral wording ("search the web", "ask with the question tool").
