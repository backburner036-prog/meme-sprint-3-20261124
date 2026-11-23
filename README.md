# Meme Sprint 3: AI Agent Goes Rogue

![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)
![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/backburner036-prog/meme-sprint-3-20261124/rank.svg)
![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/backburner036-prog/meme-sprint-3-20261124/reward.svg)

Entry for [Meme Sprint 3: AI Agent Goes Rogue on make.fun](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6).

A program that draws one image meme about an AI agent gone rogue and writes
it to `/output/entry.png` (1024×1024 PNG, well under the 1 MiB gate).

The joke: a coding agent asked to fix ONE bug "fixes" it by deleting the
entire app — then proudly reports "0 BUGS" on its laptop while the app
smoulders in the trash.

Run with Python 3.13: `python3 main.py`. Pure stdlib only (the sandbox is
`python:3.13-slim`: no PIL, no network) — the PNG is encoded by hand and
the text is drawn from a small 5×7 bitmap font.
