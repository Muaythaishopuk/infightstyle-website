# fightcard: fight-night running order

Builds the **Running order** tab of an event spreadsheet from its *Undercard* and *Main card*
tabs:

- puts every bout in class order (set per event: N, then C, then B, then A);
- puts each gym in one corner for the whole night, with any gyms or fighters you name
  kept in the red corner;
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
  --source "Undercard - =undercard.json" --source "Main card =main.json" \
  --out payload.json --sheet-id 211120
```

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
| `pytest` | 100% line and branch coverage required |
| `jscpd` | zero duplicated blocks (threshold 0%, 3 lines / 25 tokens) |

Install the tools with `pip install -e ".[dev]"`; `jscpd` runs through `npx`.
