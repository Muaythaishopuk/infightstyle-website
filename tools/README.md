# fightcard: fight-night running order

Builds three things for a fight night from the event spreadsheet:

1. the **Running order** tab;
2. the **Weigh in** tab for the weigh-in coordinator (last bout first, red then blue, with
   weight, allowance, limit, a box for the recorded weight and a Yes/No result);
3. the public **running-order post** for Instagram (main and co-main event at the top, larger,
   then every other bout down to the first; fighter names only).

The running order:

- puts every bout in class order (set per event: N, then C, then B, then A);
- puts each gym in one corner for the whole night, with any gyms or fighters you name
  kept in the red corner;
- applies ordering rules: `pinned_bouts` fixes a fighter's bout to a fight number, and
  `gym_gaps` keeps at least that many other fights between a gym's bouts (bouts stay in
  their class; otherwise the current order is kept as far as possible);
- works out start and finish times from the start time and each class's slot length.

The times in the sheet are formulas. Change the yellow **Start time** or **Minutes per bout**
cells and every time updates.

## Settings for an event

One JSON file per event in `events/`. Copy the last one for a new event and change the
start time, slot lengths, tab names, column positions (counting from 0) and the
`red_corner_gyms` / `red_corner_fighters` lists. A tab with `"billing": "headliner_first"`
lists the main event at the top, so it is fought last.

## Running it

Save each source tab as returned by the Google Sheets `get_values` tool, then:

```bash
python3 -m fightcard events/2026-11-21-fight-league-1.json \
  --source "Running order=running.json" \
  --source "Undercard - =undercard.json" --source "Main card =main.json" \
  --out payload.json --sheet-id 211120
```

Add `--weigh-in-sheet-id 211121` for the weigh-in formatting, and
`--poster-background bg.jpg --poster-out post.jpg` for the post. Weights come from the tabs
listed under `weigh_in.weight_sources`; allowances default to 0.5 kg with per-fighter
exceptions in `allowance_overrides_kg`.

It prints the running order and any warnings (TBC fighters, same gym in both corners).
`payload.json` holds the cells for `update_formulas` and the formatting for
`update_spreadsheet`. The same input always gives the same output, so the tab can be
rebuilt whenever the card changes.

## Quality gates

`./check.sh` runs all of them; each must pass before a commit:

| Gate | Standard |
|---|---|
| `ruff format` | one code style everywhere |
| `ruff check` | every rule set enabled (`select = ["ALL"]`) |
| `mypy --strict` | full type annotations, no `Any` leaks |
| `pytest` | 100% line and branch coverage required, including a rebuild-from-own-output check |
| `jscpd` | zero duplicated blocks (threshold 0%, 3 lines / 25 tokens) |

Install the tools with `pip install -e ".[dev]"`; `jscpd` runs through `npx`.
