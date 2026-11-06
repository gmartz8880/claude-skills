# docs-to-skill

Turns a documentation website into a finished skill that passes the skill-forge quality gate.

How it works: Skill Seekers scrapes the docs (no AI enhancement, no API key). Claude then rewrites
SKILL.md, records the docs license in references/SOURCE.md, and fills in the evals. skill-forge's own
scripts validate, package and install the result, and it is published only when the docs license
allows redistribution.

Needs: Python 3.10+, internet, and the skill-forge skill. scripts/setup_env.py installs Skill Seekers
if it is missing.

Try: "Convert https://click.palletsprojects.com/ into a skill"
