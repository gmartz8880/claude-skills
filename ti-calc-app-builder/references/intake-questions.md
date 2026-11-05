# Intake questions (one round)

Ask with the question tool. Up to 4 multiple-choice questions per card; add free-text questions after.
Skip anything the request already answers. Always offer "You pick" so the user can delegate.

## Card 1 (multiple choice)

1. **Which calculator?** - TI-Nspire CAS / TI-84 Plus CE / Both (same app on each)
2. **Which TI-Nspire CAS exactly?** (only if Nspire chosen and not already known)
   - CX II CAS (color, 2019+, OS 5 or 6) - Lua, Python, TI-Basic
   - CX CAS (color, OS 3-4) - Lua, TI-Basic
   - Original CAS (black-and-white screen) - Lua (OS 3.0.2+), TI-Basic
   - Not sure - "Home > Settings > Status (or About) shows the model and OS"
3. **What kind of app?** - Math/science tool (formulas, solvers, converters) / Game / Study aid (notes,
   flashcards, quizzes, reference tables) / Utility (timer, unit converter, checklist, data logger)
4. **Stock calculator or jailbreak OK?**
   - Stock only (TI-BASIC / Lua / Python) - works on every unit, nothing to install
   - Jailbreak OK (C on TI-84 Plus CE via arTIfiCE when OS >= 5.5; Ndless C on Nspire) - fastest, more setup
   - You pick (default: stock, unless the app needs speed only C can give)

## Card 2 (free text, short)

5. **What should the app do?** One or two sentences, plus any must-have features.
   Example: "Solve projectile motion: enter angle and speed, show range, max height, and time."
6. **Inputs and outputs.** What does the user type, what should the screen show, and in which units?
7. **Look and feel (optional).** Colors, dark mode, big text, sounds (none available on these models), graph or text.
8. **TI-84 Plus CE details** (only if CE chosen and unknown): OS version ([2nd][mem] 1:About) and
   whether a "Python App" appears under [apps].

## Defaults when the user does not say
- Both calculators get the same features and controls.
- Feature pack: help screen, about screen, saved settings, dark/light toggle, input validation, clean exit.
- Language from the decision table in `platforms.md`.
- App name derived from the purpose (CE: 8 chars max, A-Z 0-9, starts with a letter).

## After intake
Summarize the choices in 3-6 lines (the spec) and start building in the same turn.
