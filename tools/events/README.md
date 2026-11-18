# Event settings

`2026-11-21-fight-league-1.json` first built the Running order tab from the *Undercard - *
and *Main card * tabs (see git history). The card was then edited by hand on the Running
order tab, so that tab is now its own source: rebuilding reads it, keeps those edits,
re-applies the corner rules and recalculates the timings and intervals.
